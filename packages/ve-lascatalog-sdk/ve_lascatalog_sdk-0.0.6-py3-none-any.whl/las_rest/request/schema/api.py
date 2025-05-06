from http.client import responses

from las_rest.core.api import LasTopApi
from las_rest.request.catalog.model import AlterCatalogRequest

LIST_SCHEMA = "ListSchema"
LIST_SCHEMA_NAMES = "ListSchemaNames"
GET_SCHEMA = "GetSchema"
CREATE_SCHEMA = "CreateSchema"
DROP_SCHEMA = "DropSchema"
ALTER_SCHEMA = "AlterSchema"


class SchemaApi(LasTopApi):
    name = 'SchemaApi'

    def __init__(self, api_client=None,
                 service_name="las",
                 region="cn-beijing", version="2024-04-30", env="online"):
        super(SchemaApi, self).__init__(api_client=api_client,
                                        service_name=service_name, region=region,
                                        version=version, env=env)

    def list_schema(self, catalog_name, offset=1, limit=20):
        req_params = dict({
            "CatalogName": catalog_name,
            "Offset": offset,
            "Limit": limit
        }, **self.create_request_params(LIST_SCHEMA_NAMES))
        response = self._call_get_method(req_params=req_params)
        return response

    def get_schema(self, schema_name, catalog_name):
        req_params = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name
        }, **self.create_request_params(LIST_SCHEMA))
        response = self._call_get_method(req_params=req_params)
        return response

    def create_schema(self, location, schema_name, catalog_name, description=''):
        req_params = self.create_request_params(CREATE_SCHEMA)
        req_body = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "Location": location,
            "Description": description
        })
        response = self._call_post_method(req_params=req_params, body=req_body)
        return response

    def drop_schema(self, schema_name, catalog_name):
        req_params = self.create_request_params(DROP_SCHEMA)
        req_body = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name
        })
        response = self._call_post_method(req_params=req_params, body=req_body)
        return response

    def alter_schema(self, location, schema_name, catalog_name, description=''):
        req_params = self.create_request_params(ALTER_SCHEMA)
        req_body = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "Location": location,
            "Description": description
        })
        response = self._call_post_method(req_params=req_params, body=req_body)
        return response
