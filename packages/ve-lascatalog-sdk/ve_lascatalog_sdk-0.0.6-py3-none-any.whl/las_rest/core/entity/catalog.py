import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class Catalog:
    catalog_name: str
    owner: str
    description: str
    location: str
    create_time: str
    update_time: str
    allow_deletion: bool
    allow_edition: bool
    region: Optional[str] = None

    @classmethod
    def from_json(cls, json_str: str) -> 'Catalog':
        """从JSON字符串创建Catalog对象"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> 'Catalog':
        """从字典中创建Catalog对象，处理API返回的大驼峰格式"""
        field_mapping = {
            'CatalogName': 'catalog_name',
            'Owner': 'owner',
            'Description': 'description',
            'Location': 'location',
            'CreateTime': 'create_time',
            'UpdateTime': 'update_time',
            'AllowDeletion': 'allow_deletion',
            'AllowEdition': 'allow_edition',
            'Region': 'region'
        }

        converted_data = {}
        for api_key, class_key in field_mapping.items():
            if api_key in data:
                converted_data[class_key] = data[api_key]

        return cls(**converted_data)

    def to_json(self) -> str:
        """将Catalog对象序列化为JSON字符串"""
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        """将Catalog对象转换为符合API格式的字典（大驼峰）"""
        field_mapping = {
            'catalog_name': 'CatalogName',
            'owner': 'Owner',
            'description': 'Description',
            'location': 'Location',
            'create_time': 'CreateTime',
            'update_time': 'UpdateTime',
            'allow_deletion': 'AllowDeletion',
            'allow_edition': 'AllowEdition',
            'region': 'Region'
        }

        return {
            field_mapping[key]: value
            for key, value in self.__dict__.items()
            if value is not None
        }

    @classmethod
    def parse_response(cls, response: Dict[str, Any]) -> List[
        'Catalog']:
        """
        解析API响应，返回Catalog对象列表
        """
        # 获取数据，如果不存在返回空列表
        if response is None:
            return []
        data_list = response.get("Result", {}).get("Data", [])

        # 如果没有数据，返回空列表
        if not data_list:
            return []

        # 转换每个数据项为Catalog对象
        catalogs = []
        for item in data_list:
            try:
                catalog = Catalog.from_dict(item)
                catalogs.append(catalog)
            except Exception as e:
                print(f"解析数据失败: {str(e)}, data: {item}")
                continue
        return catalogs
