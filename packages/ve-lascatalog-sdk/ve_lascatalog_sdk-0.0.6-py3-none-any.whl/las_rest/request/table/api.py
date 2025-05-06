from typing import Dict, Any, List

from las_rest.core.api import LasTopApi
from las_rest.utils.tool import update_dict

LIST_TABLES_NAMES = "ListTableNames"
GET_TABLE_DETAIL = "GetTableDetail"
CREATE_TABLE = "CreateTable"
ALTER_TABLE = "AlterTable"
DROP_TABLE = "DropTable"


class TableApi(LasTopApi):
    name = 'TableApi'

    def __init__(self, api_client=None, scheme="https", host="open.volcengineapi.com", service_name="las",
                 region="cn-beijing", version="2024-04-30", env="online"):
        super(TableApi, self).__init__(api_client, scheme=scheme, host=host, service_name=service_name,
                                       region=region,
                                       version=version, env=env)

    def list_tables(self, catalog_name, schema_name, offset=1, limit=20):
        base_request_params = self.create_request_params(LIST_TABLES_NAMES)
        req_params = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "Offset": offset,
            "Limit": limit
        }, **base_request_params)
        response = self._call_get_method(req_params=req_params)
        return response

    def get_table(self, catalog_name, schema_name, table_name):
        base_request_params = self.create_request_params(GET_TABLE_DETAIL)
        req_params = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "TableName": table_name
        }, **base_request_params)
        response = self._call_get_method(req_params=req_params)
        return response

    def create_table(self, table: Dict[str, Any]):
        base_request_params = self.create_request_params(CREATE_TABLE)
        response = self._call_post_method(req_params=base_request_params, body=table)
        return response

    def alter_table(self, table: Dict[str, Any]):
        base_request_params = self.create_request_params(ALTER_TABLE)
        response = self._call_post_method(req_params=base_request_params, body=table)
        return response

    def drop_table(self, catalog_name, schema_name, table_name):
        base_request_params = self.create_request_params(DROP_TABLE)
        req_body = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "TableName": table_name
        })
        response = self._call_post_method(req_params=base_request_params, body=req_body)
        return response

    @classmethod
    def parse_table_response(cls, response: Dict[str, Any]) -> List[str]:
        """
        解析API响应，返回Database对象列表
        """
        if response is None:
            return []
        data_list = response.get("Result", {}).get("Data", [])
        return data_list
