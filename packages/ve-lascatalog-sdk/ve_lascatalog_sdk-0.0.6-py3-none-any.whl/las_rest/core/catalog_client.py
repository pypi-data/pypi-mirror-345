import logging
import os
from time import sleep
from typing import Callable, TypeVar, List, Dict, Any

from las_rest.core.client import ApiClient
from las_rest.core.entity.database import Database
from las_rest.core.entity.table import Table
from las_rest.core.entity.catalog import Catalog
from las_rest.request.catalog.api import CatalogApi
from las_rest.request.schema.api import SchemaApi
from las_rest.request.table.api import TableApi
from las_rest.request.optimizer.api import OptimizerApi

T = TypeVar('T')

# 配置基本的日志格式和级别
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 获取 logger
logger = logging.getLogger(__name__)
env_list = ['online','testing','staging','preview']

def fetch_all(api_func: Callable[..., Dict[str, Any]],  # 使用 ... 表示可变参数
              response_parser: Callable[[Dict[str, Any]], List[T]],
              page_size: int = 100,
              max_retries: int = 1,
              retry_delay: float = 1.0,
              **api_kwargs: Any  # 接收额外的API参数
              ) -> List[T]:
    """
    获取分页API的所有数据

    Args:
        api_func: 调用API的函数，必须接受limit和offset参数，可以有其他参数
        response_parser: 解析响应的函数，返回数据列表
        page_size: 每页数据量
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        api_kwargs: 传递给api_func的额外参数
    """

    all_results: List[T] = []
    offset = 1
    retry_count = 0

    while True:
        try:
            # 调用API获取一页数据，合并所有参数
            response = api_func(
                limit=page_size,
                offset=offset,
                **api_kwargs  # 传入额外的参数
            )
            page_data = response_parser(response)

            # 重置重试计数
            retry_count = 0

            if not page_data:
                break

            all_results.extend(page_data)
            offset += len(page_data)
            if len(page_data) < page_size:
                break

        except Exception as e:
            retry_count += 1
            if retry_count > max_retries:
                raise Exception(f"达到最大重试次数 ({max_retries}): {str(e)}")

            logging.warning(
                f"fetch metadata error  (retry {retry_count}/{max_retries}): {str(e)}")
            sleep(retry_delay)

    return all_results


class CatalogClient:
    def __init__(self,
                 access_key: str = None,
                 secret_key: str = None,
                 sts_token: str = None,
                 region: str = None,
                 catalog_name: str = 'hive'):
        # 初始化API客户端
        self._api_client = ApiClient(access_key, secret_key, sts_token)
        self._catalog_name = catalog_name
        environment = os.getenv('CATALOG_ENVIRONMENT')
        if environment is None or environment not in env_list:
            environment = 'online'

        # 初始化各个API组件
        self._database_api = SchemaApi(api_client=self._api_client,
                                       region=region,
                                       env=environment)
        self._table_api = TableApi(api_client=self._api_client, region=region,
                                   env=environment)
        self._catalog_api = CatalogApi(api_client=self._api_client, region=region,
                                       env=environment)
        self._optimizer_api = OptimizerApi(api_client=self._api_client, region=region,
                                         env=environment)

    def list_catalogs(self) -> List[Catalog]:
        return fetch_all(
            api_func=self._catalog_api.list_catalogs,
            response_parser=Catalog.parse_response,
        )

    def get_catalog(self, catalog_name) -> Catalog:
        """获取数据目录"""
        response = self._catalog_api.get_catalog(catalog_name)
        if response is None or response.get('ResponseMetadata') is None:
            raise Exception("Response is None or ResponseMetadata is None")
        if response.get('ResponseMetadata').get('Error') is not None and len(
                response.get('ResponseMetadata').get('Error')) > 0:
            error_msg = response['ResponseMetadata'].get('Error')
            logger.error("Error getting catalogs: %s", error_msg)
            raise Exception(f"Error getting catalogs: {error_msg}")
        return Catalog.from_dict(response['Result'])

    def create_catalog(self, catalog_name, location, description) -> bool:
        """创建数据目录"""
        response = self._catalog_api.create_catalog(catalog_name, location, description)
        if response is None or response.get('ResponseMetadata') is None:
            raise Exception("Failed to create catalog: Response or ResponseMetadata is None.")
        if response.get('ResponseMetadata').get('Error') is not None and len(
                response.get('ResponseMetadata').get('Error')) > 0:
            error_msg = response['ResponseMetadata']['Error']
            logger.error("create catalog error %s", error_msg)
            raise Exception(f"Failed to create catalog: {error_msg}")
        return True

    def drop_catalog(self, catalog_name) -> bool:
        """删除数据目录"""
        response = self._catalog_api.drop_catalog(catalog_name)
        if response is None or response.get('Result') is None:
            raise Exception("Failed to drop catalog: Response or Result is None.")
        if response.get('Result').get('ErrorMessage') is not None and len(
                response.get('Result').get('ErrorMessage')) > 0:
            error_msg = response.get('Result').get('ErrorMessage')
            logger.error("drop catalog error %s", error_msg)
            raise Exception(f"Failed to drop catalog: {error_msg}")
        return True

    def get_all_databases(self, catalog_name: str = None) -> List[str]:
        """获取所有数据库"""
        if catalog_name is None:
            catalog_name = self._catalog_name
        return fetch_all(
            api_func=self._database_api.list_schema,
            response_parser=Database.parse_response,
            catalog_name=catalog_name
        )

    def get_database(self, db_name: str, catalog_name: str = None) -> Database:
        """获取指定数据库"""
        if catalog_name is None:
            catalog_name = self._catalog_name
        response = self._database_api.get_schema(db_name, catalog_name)
        if response is None or response.get('ResponseMetadata') is None:
            raise Exception(
                f"Failed to get database {db_name} in catalog {catalog_name}: Response is None or ResponseMetadata is None.")
        if response.get('ResponseMetadata').get('Error') is not None and len(
                response.get('ResponseMetadata').get('Error')) > 0:
            error_msg = response['ResponseMetadata']['Error']
            logger.error("get catalog error %s", error_msg)
            raise Exception(f"Failed to get database {db_name} in catalog {catalog_name}: {error_msg}")
        return Database.from_dict(response)

    def create_database(self, database: Database) -> bool:
        """创建数据库"""
        response = self._database_api.create_schema(database.location, database.name, database.catalog_name,
                                                    database.description)
        if response is None or response.get('ResponseMetadata') is None:
            raise Exception("Failed to create database: Response or ResponseMetadata is None.")
        if response.get('ResponseMetadata').get('Error') is not None and len(
                response.get('ResponseMetadata').get('Error')) > 0:
            error_msg = response['ResponseMetadata']['Error']
            logger.error("create database error %s", error_msg)
            raise Exception(f"Failed to create database: {error_msg}")
        return True

    def drop_database(self, database_name: str, catalog_name: str) -> bool:
        """删除数据库"""
        response = self._database_api.drop_schema(database_name, catalog_name)
        if response is None or response.get('Result') is None:
            # 当响应或响应结果为空时，抛出异常
            raise Exception(
                f"Failed to drop database {database_name} in catalog {catalog_name}: Response or Result is None.")
        if response.get('Result').get("ErrorMessage") is not None and len(response.get('Result').get("ErrorMessage")) > 0:
            error_msg = response.get('Result').get("ErrorMessage")
            logger.error("drop database error %s", error_msg)
            # 当结果中存在错误信息时，抛出异常
            raise Exception(f"Failed to drop database {database_name} in catalog {catalog_name}: {error_msg}")
        return True

    def alter_database(self, database: Database) -> bool:
        """修改数据库"""
        response = self._database_api.alter_schema(database.location, database.name, database.catalog_name,
                                                   database.description)
        if response is None or response.get('ResponseMetadata') is None:
            # 当响应或响应元数据为空时，抛出异常
            raise Exception("Failed to alter database: Response or ResponseMetadata is None.")
        if response.get('ResponseMetadata').get('Error') is not None and len(response.get('ResponseMetadata').get('Error')) > 0:
            error_msg = response['ResponseMetadata']['Error']
            logger.error("alter database error %s", error_msg)
            # 当响应元数据中存在错误信息时，抛出异常
            raise Exception(f"Failed to alter database: {error_msg}")
        return True

    def get_all_tables(self, database: str, catalog_name) -> List[str]:
        """获取指定数据库中的所有表"""
        if catalog_name is None:
            catalog_name = self._catalog_name
        return fetch_all(
            api_func=self._table_api.list_tables,
            response_parser=Table.parse_response,
            schema_name=database,
            catalog_name=catalog_name,
        )

    def get_table(self, table_name: str, database: str, catalog_name: str = None, ) -> Table:
        """获取指定表"""
        if catalog_name is None:
            catalog_name = self._catalog_name
        response = self._table_api.get_table(catalog_name, database, table_name)
        if response is None or response.get('ResponseMetadata') is None:
            raise Exception(
                f"Failed to get table {table_name} in database {database} of catalog {catalog_name}: Response is None or ResponseMetadata is None.")
        if response.get('ResponseMetadata').get('Error') is not None and len(response.get('ResponseMetadata').get('Error')) > 0:
            error_msg = response['ResponseMetadata']['Error']
            logger.error("get table error %s", error_msg)
            raise Exception(
                f"Failed to get table {table_name} in database {database} of catalog {catalog_name}: {error_msg}")
        if response.get('Result') is None:
            return None
        return Table.from_dict(response.get('Result'))

    def get_table_objects_by_name(self, catalog_name: str, database: str, tables: List[str]) -> \
            List[Table]:
        """根据数据集名称获取表对象"""
        if catalog_name is None:
            catalog_name = self._catalog_name
        res = []
        for tbl in tables:
            res.append(self.get_table(table_name=tbl, database=database, catalog_name=catalog_name))
        return res

    def get_table_objects_by_location(self, catalog_name: str, database: str, locations: str) -> \
            Table:
        return None

    def create_table(self, table: Table) -> bool:
        """创建表"""
        response = self._table_api.create_table(table.to_dict())
        if response is None or response.get('ResponseMetadata') is None:
            # 当响应或响应元数据为空时，抛出异常
            raise Exception("Failed to create table: Response or ResponseMetadata is None.")
        if response.get('ResponseMetadata').get('Error') is not None and len(
                response.get('ResponseMetadata').get('Error')) > 0:
            error_msg = response['ResponseMetadata']['Error']
            logger.error("create table error %s", error_msg)
            # 当响应元数据中存在错误信息时，抛出异常
            raise Exception(f"Failed to create table: {error_msg}")
        return True

    def alter_table(self, table: Table) -> bool:
        """修改表"""
        response = self._table_api.alter_table(table.to_dict())
        if response is None or response.get('ResponseMetadata') is None:
            # 当响应或响应元数据为空时，抛出异常
            raise Exception("Failed to alter table: Response or ResponseMetadata is None.")
        if response.get('ResponseMetadata').get('Error') is not None and len(response.get('ResponseMetadata').get('Error')) > 0:
            error_msg = response['ResponseMetadata']['Error']
            logger.error("alter table error %s", error_msg)
            # 当响应元数据中存在错误信息时，抛出异常
            raise Exception(f"Failed to alter table: {error_msg}")
        return True

    def drop_table(self, catalog: str, database: str, table_name: str) -> bool:
        """删除表"""
        response = self._table_api.drop_table(catalog, database, table_name)
        if response is None or response.get('ResponseMetadata') is None:
            raise Exception(
                f"Failed to drop table {table_name} in database {database} of catalog {catalog}: Response is None or ResponseMetadata is None.")
        if response.get('Result').get('ErrorMessage') is not None and len(
                response.get('Result').get('ErrorMessage')) > 0:
            error_msg = response.get('Result').get('ErrorMessage')
            logger.error("drop table error %s", error_msg)
            raise Exception(
                f"Failed to drop table {table_name} in database {database} of catalog {catalog}: {error_msg}")
        return True

    def update_optimizer_task(self, catalog: str, database: str, table_name: str, type: str, taskId: int, task_detail: dict) -> bool:
        """修改任务优化"""
        response = self._optimizer_api.update_optimizer_task(catalog, database, table_name, type, taskId, task_detail)
        if response is None or response.get('ResponseMetadata') is None:
            raise Exception(
                f"Failed to update optimizer task for catalog {catalog}, database {database}, table {table_name}, type {type}, taskId {taskId}. Response or ResponseMetadata is None.")
        if response.get('ResponseMetadata').get('Error') is not None and len(
                response.get('ResponseMetadata').get('Error')) > 0:
            error_msg = response['ResponseMetadata']['Error']
            logger.error("alter optimizertask error %s", error_msg)
            raise Exception(
                f"Failed to update optimizer task for catalog {catalog}, database {database}, table {table_name}, type {type}, taskId {taskId}. Error: {error_msg}")
        return True
