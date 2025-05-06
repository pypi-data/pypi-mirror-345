from datetime import datetime
from typing import Optional

from las_rest.core.entity.database import Database


class DatabaseBuilder:
    """Builds Database object with flexible parameter configuration."""

    def __init__(
            self,
            name: str,
            location: str,
            catalog_name: str,
    ):
        """
        Initialize DatabaseBuilder with required parameters.

        :param name: Database name
        :param location: Physical location of the database
        :param catalog_name: Name of the catalog
        """
        self.name = name
        self.location = location
        self.catalog_name = catalog_name

        self.description = ""
        self.table_count = "0"
        self.owner = ""
        self.source_type = ""
        self.region = ""
        self.permission = None
        self.storage = "0"
        self.resource_count = None
        self.udf_count = None
        self.env = "Preview"
        self.size_update_time = datetime.now()
        self.is_metadata = False
        self.allow_deletion = True
        self.allow_edition = True
        self.ttl_enabled = False
        self.ttl_days = 0
        self.ttl_hot_days = 0
        self.tiered_storage_strategy = None
        self.create_time = datetime.now()
        self.update_time = datetime.now()

    def with_description(self, description: str) -> 'DatabaseBuilder':
        """Set database description."""
        self.description = description
        return self

    def with_storage(self, storage: str) -> 'DatabaseBuilder':
        """Set storage information."""
        self.storage = storage
        return self

    def with_env(self, env: str) -> 'DatabaseBuilder':
        """Set environment."""
        self.env = env
        return self

    def with_metadata_flag(self, is_metadata: bool) -> 'DatabaseBuilder':
        """Set metadata flag."""
        self.is_metadata = is_metadata
        return self

    def with_edition_flag(self, allow_edition: bool) -> 'DatabaseBuilder':
        """Set edition permission flag."""
        self.allow_edition = allow_edition
        return self

    def with_tiered_storage_strategy(self, strategy: Optional[str]) -> 'DatabaseBuilder':
        """Set tiered storage strategy."""
        self.tiered_storage_strategy = strategy
        return self

    def with_timestamps(self, create_time: datetime, update_time: datetime) -> 'DatabaseBuilder':
        """Set creation and update timestamps."""
        self.create_time = create_time
        self.update_time = update_time
        return self

    def build(self) -> 'Database':
        """
        Build and return the Database object.
        """
        return Database(
            region=self.region,
            source_type=self.source_type,
            name=self.name,
            owner=self.owner,
            description=self.description,
            table_count=self.table_count,
            permission=self.permission,
            storage=self.storage,
            resource_count=self.resource_count,
            udf_count=self.udf_count,
            env=self.env,
            size_update_time=self.size_update_time,
            is_metadata=self.is_metadata,
            allow_deletion=self.allow_deletion,
            allow_edition=self.allow_edition,
            ttl_enabled=self.ttl_enabled,
            ttl_days=self.ttl_days,
            ttl_hot_days=self.ttl_hot_days,
            tiered_storage_strategy=self.tiered_storage_strategy,
            location=self.location,
            catalog_name=self.catalog_name,
            create_time=self.create_time,
            update_time=self.update_time
        )
