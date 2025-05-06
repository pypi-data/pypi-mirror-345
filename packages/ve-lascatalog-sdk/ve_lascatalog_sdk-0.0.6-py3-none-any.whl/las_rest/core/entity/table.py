import json
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Any


class TableType(Enum):
    MANAGED_TABLE = "MANAGED_TABLE"
    EXTERNAL_TABLE = "EXTERNAL_TABLE"
    VIRTUAL_VIEW = "VIRTUAL_VIEW"

    @classmethod
    def from_str(cls, value: str) -> 'TableType':
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid TableType value: {value}")


class FileFormat(Enum):
    PARQUET = "Parquet"
    ORC = "ORC"
    AVRO = "Avro"
    TEXTFILE = "TextFile"
    SEQUENCEFILE = "SequenceFile"
    RCFILE = "RcFile"
    JSON = "JSON"
    CSV = "CSV"
    LANCE = "Lance"
    ICEBERG = "Iceberg"
    PAIMON = "Paimon"

    @classmethod
    def from_str(cls, value: str) -> 'FileFormat':
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid FileFormat value: {value}")


class PartitionType(Enum):
    PARTITION = "PARTITION"
    NON_PARTITION = "NON_PARTITION"

    @classmethod
    def from_str(cls, value: str) -> 'PartitionType':
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid PartitionType value: {value}")


@dataclass
class FieldColumn:
    column_name: str
    column_type: str
    column_desc: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "ColumnName": self.column_name,
            "ColumnType": self.column_type,
            "ColumnDesc": self.column_desc
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FieldColumn':
        return cls(
            column_name=data["ColumnName"],
            column_type=data["ColumnType"],
            column_desc=data.get("ColumnDesc")
        )


@dataclass
class Table:
    database_name: str
    table_name: str
    partition_type: PartitionType
    field_columns: List[FieldColumn]
    catalog_name: Optional[str] = None
    table_type: Optional[TableType] = None
    file_format: Optional[FileFormat] = None
    table_comment: Optional[str] = None
    location: Optional[str] = None
    partition_columns: Optional[List[FieldColumn]] = None
    table_properties: Optional[Dict[str, str]] = None
    ttl_enabled: Optional[bool] = None
    ttl_days: Optional[int] = None
    tiered_storage_strategy: Optional[str] = None

    def __post_init__(self):
        if self.partition_type == PartitionType.PARTITION and not self.partition_columns:
            raise ValueError("Partition columns are required for partition tables")

    def to_dict(self) -> dict:
        """Convert Table object to dictionary using PascalCase keys"""
        result = {
            "SchemaName": self.database_name,
            "CatalogName": self.catalog_name,
            "TableName": self.table_name,
            "PartitionType": self.partition_type.value,
            "FieldColumns": [col.to_dict() for col in self.field_columns]
        }

        if self.table_type is not None:
            result["TableType"] = self.table_type.value
        if self.file_format is not None:
            result["FileFormat"] = self.file_format.value
        if self.table_comment is not None:
            result["TableComment"] = self.table_comment
        if self.location is not None:
            result["Location"] = self.location
        if self.partition_columns is not None:
            result["PartitionColumns"] = [col.to_dict() for col in self.partition_columns]
        if self.table_properties is not None:
            result["TableProperties"] = self.table_properties
        if self.ttl_enabled is not None:
            result["TtlEnabled"] = self.ttl_enabled
        if self.ttl_days is not None:
            result["TtlDays"] = self.ttl_days
        if self.tiered_storage_strategy is not None:
            result["TieredStorageStrategy"] = self.tiered_storage_strategy

        return result

    def to_json(self, indent: int = 2) -> str:
        """Convert Table object to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> 'Table':
        """Create Table object from dictionary with PascalCase keys"""
        if data.get("FieldColumns") is None:
            return None
        field_columns = [FieldColumn.from_dict(col) for col in data["FieldColumns"]]

        # Convert partition_columns if they exist
        partition_columns = None
        if "PartitionColumns" in data:
            partition_columns = [FieldColumn.from_dict(col) for col in data["PartitionColumns"]]

        # Convert enum types
        partition_type = PartitionType.from_str(data["PartitionType"])
        table_type = TableType.from_str(data["TableType"]) if "TableType" in data else None
        file_format = FileFormat.from_str(data["FileFormat"]) if "FileFormat" in data else None
        tiered_storage_strategy = data["TieredStorageStrategy"] if "TieredStorageStrategy" in data else None

        # Helper function to handle '-' values
        def get_value(data: dict, key: str) -> Any:
            value = data.get(key)
            return None if value == '-' else value

        return cls(
            database_name=data["SchemaName"],
            table_name=data["TableName"],
            partition_type=partition_type,
            field_columns=field_columns,
            catalog_name=get_value(data, "CatalogName"),
            table_type=table_type,
            file_format=file_format,
            table_comment=get_value(data, "TableComment"),
            location=get_value(data, "Location"),
            partition_columns=partition_columns,
            table_properties=get_value(data, "TableProperties"),
            ttl_enabled=get_value(data, "TtlEnabled"),
            ttl_days=get_value(data, "TtlDays"),
            tiered_storage_strategy=tiered_storage_strategy
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'Table':
        """Create Table object from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def parse_response(cls, response: str) -> List['Table']:
        if response is None:
            return []
        data_list = response.get("Result", {}).get("Data", [])
        return data_list
