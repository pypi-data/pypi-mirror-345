from las_rest.core.api import LasTopApi
from las_rest.request.catalog.model import AlterCatalogRequest

GET_CATALOG = "GetCatalog"
LIST_CATALOGS = "ListCatalogs"
LIST_CATALOG_NAMES = "ListCatalogNames"
CREATE_CATALOG = "CreateCatalog"
ALTER_CATALOG = "AlterCatalog"
DROP_CATALOG = "DropCatalog"

class CatalogApi(LasTopApi):
    name = 'CatalogApi'

    def __init__(self, api_client, scheme="https", host="open.volcengineapi.com", service_name="las",
                 region="cn-beijing", version="2024-04-30", env="online"):
        super(CatalogApi, self).__init__(api_client, scheme=scheme, host=host, service_name=service_name, region=region,
                                         version=version, env=env)

    def get_catalog(self, catalog_name):
        req_params = dict({
            "CatalogName": catalog_name
        }, **self.create_request_params(GET_CATALOG))
        response = self._call_get_method(req_params=req_params)
        return response

    def list_catalogs(self, offset=1, limit=20):
        req_params = dict({
            "Offset": offset,
            "Limit": limit
        }, **self.create_request_params(LIST_CATALOGS))
        response = self._call_get_method(req_params=req_params)
        return response

    def list_catalog_names(self, offset=1, limit=20):
        req_params = dict({
            "Offset": offset,
            "Limit": limit
        }, **self.create_request_params(LIST_CATALOG_NAMES))
        response = self._call_get_method(req_params=req_params)
        return response

    def create_catalog(self, catalog_name, location, description):
        req_params = self.create_request_params(CREATE_CATALOG)
        post_params = {
            "CatalogName": catalog_name,
            "location": location,
            "Description": description
        }
        response = self._call_post_method(req_params, post_params)
        return response
    def drop_catalog(self, catalog_name):
        req_params = self.create_request_params(DROP_CATALOG)
        post_params = {
            "CatalogName": catalog_name,
        }
        response = self._call_post_method(req_params, post_params)
        return response
    def alter_catalog(self, alter_catalog_request: AlterCatalogRequest):
        req_params = self.create_request_params(ALTER_CATALOG)
        response = self._call_post_method(req_params, alter_catalog_request.model_to_dict())
        return response
