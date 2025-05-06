from dataclasses import dataclass
from typing import Optional, Dict, List, Any
from datetime import datetime


@dataclass
class Database:
    region: str
    source_type: str
    name: str
    owner: str
    description: str
    table_count: str
    permission: Optional[str]
    storage: str
    resource_count: Optional[str]
    udf_count: Optional[str]
    env: str
    size_update_time: datetime
    is_metadata: bool
    allow_deletion: bool
    allow_edition: bool
    ttl_enabled: bool
    ttl_days: int
    ttl_hot_days: int
    tiered_storage_strategy: Optional[str]
    location: str
    catalog_name: str
    create_time: datetime
    update_time: datetime

    @classmethod
    def from_dict(cls, data: dict) -> 'Database':
        """
        从字典创建实例的工厂方法
        """
        data = data.get('Result', {}).get('Data', {})
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        elif not isinstance(data, dict):
            return None
        return cls(
            region=data.get('Region'),
            source_type=data.get('SourceType'),
            name=data.get('Name'),
            owner=data.get('Owner'),
            description=data.get('Description'),
            table_count=data.get('TableCount'),
            permission=data.get('Permission'),
            storage=data.get('Storage'),
            resource_count=data.get('ResourceCount'),
            udf_count=data.get('UdfCount'),
            env=data.get('Env'),
            size_update_time=datetime.strptime(data.get('SizeUpdateTime', ''), '%Y-%m-%d %H:%M:%S') if data.get(
                'SizeUpdateTime') else None,
            is_metadata=data.get('IsMetadata'),
            allow_deletion=data.get('AllowDeletion'),
            allow_edition=data.get('AllowEdition'),
            ttl_enabled=data.get('TtlEnabled'),
            ttl_days=data.get('TtlDays'),
            ttl_hot_days=data.get('TtlHotDays'),
            tiered_storage_strategy=data.get('TieredStorageStrategy'),
            location=data.get('Location'),
            catalog_name=data.get('CatalogName'),
            create_time=datetime.strptime(data.get('CreateTime', ''), '%Y-%m-%d %H:%M:%S') if data.get(
                'CreateTime') else None,
            update_time=datetime.strptime(data.get('UpdateTime', ''), '%Y-%m-%d %H:%M:%S') if data.get(
                'UpdateTime') else None
        )

    def to_dict(self) -> dict:
        """
        将实例转换为字典的方法
        """
        return {
            'Region': self.region,
            'SourceType': self.source_type,
            'Name': self.name,
            'Owner': self.owner,
            'Description': self.description,
            'TableCount': self.table_count,
            'Permission': self.permission,
            'Storage': self.storage,
            'ResourceCount': self.resource_count,
            'UdfCount': self.udf_count,
            'Env': self.env,
            'SizeUpdateTime': self.size_update_time.strftime('%Y-%m-%d %H:%M:%S'),
            'IsMetadata': self.is_metadata,
            'AllowDeletion': self.allow_deletion,
            'AllowEdition': self.allow_edition,
            'TtlEnabled': self.ttl_enabled,
            'TtlDays': self.ttl_days,
            'TtlHotDays': self.ttl_hot_days,
            'TieredStorageStrategy': self.tiered_storage_strategy,
            'Location': self.location,
            'CatalogName': self.catalog_name,
            'CreateTime': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'UpdateTime': self.update_time.strftime('%Y-%m-%d %H:%M:%S')
        }

    @classmethod
    def parse_response(cls, response: Dict[str, Any]) -> List[
        'Database']:
        """
        解析API响应，返回Database对象列表
        """
        # 获取数据，如果不存在返回空列表
        if response is None:
            return []
        data_list = response.get("Result", {}).get("Data", [])

        # 如果没有数据，返回空列表
        if not data_list:
            return []
        return data_list
