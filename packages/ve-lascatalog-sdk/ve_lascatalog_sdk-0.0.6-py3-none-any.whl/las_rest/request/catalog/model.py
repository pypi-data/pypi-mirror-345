from las_rest.core.model import RequestModel


class Catalog(RequestModel):

    def __init__(self, catalog_name, owner, region, description, location):
        self.catalog_name = catalog_name
        self.owner = owner
        self.region = region
        self.description = description
        self.location = location


class AlterCatalogRequest(RequestModel):

    def __init__(self, catalog_name, catalog):
        self.catalog_name = catalog_name
        self.catalog = catalog
