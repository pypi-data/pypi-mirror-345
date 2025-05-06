from typing import List, Dict

from las_rest.core.entity.table import Table, FieldColumn, FileFormat, TableType, PartitionType


class TableBuilder:
    def __init__(self):
        self._table = {
            "database_name": None,
            "table_name": None,
            "partition_type": None,
            "catalog_name": None,
            "field_columns": []
        }

    def with_database_name(self, database_name: str) -> 'TableBuilder':
        self._table["database_name"] = database_name
        return self

    def with_table_name(self, table_name: str) -> 'TableBuilder':
        self._table["table_name"] = table_name
        return self

    def with_partition_type(self, partition_type: PartitionType) -> 'TableBuilder':
        self._table["partition_type"] = partition_type
        return self

    def with_field_columns(self, field_columns: List[FieldColumn]) -> 'TableBuilder':
        self._table["field_columns"] = field_columns
        return self

    def with_catalog_name(self, catalog_name: str) -> 'TableBuilder':
        self._table["catalog_name"] = catalog_name
        return self

    def with_table_type(self, table_type: TableType) -> 'TableBuilder':
        self._table["table_type"] = table_type
        return self

    def with_file_format(self, file_format: FileFormat) -> 'TableBuilder':
        self._table["file_format"] = file_format
        return self

    def with_table_comment(self, table_comment: str) -> 'TableBuilder':
        self._table["table_comment"] = table_comment
        return self

    def with_location(self, location: str) -> 'TableBuilder':
        self._table["location"] = location
        return self

    def with_partition_columns(self, partition_columns: List[FieldColumn]) -> 'TableBuilder':
        self._table["partition_columns"] = partition_columns
        return self

    def with_table_properties(self, table_properties: Dict[str, str]) -> 'TableBuilder':
        self._table["table_properties"] = table_properties
        return self

    def with_ttl_enabled(self, ttl_enabled: bool) -> 'TableBuilder':
        self._table["ttl_enabled"] = ttl_enabled
        return self

    def with_ttl_days(self, ttl_days: int) -> 'TableBuilder':
        self._table["ttl_days"] = ttl_days
        return self

    def with_tiered_storage_strategy(self, strategy: str) -> 'TableBuilder':
        self._table["tiered_storage_strategy"] = strategy
        return self

    def build(self) -> Table:
        # Validate required fields
        if not all([self._table["database_name"],
                    self._table["table_name"],
                    self._table["partition_type"]]):
            raise ValueError("Missing required fields")

        return Table(**self._table)
