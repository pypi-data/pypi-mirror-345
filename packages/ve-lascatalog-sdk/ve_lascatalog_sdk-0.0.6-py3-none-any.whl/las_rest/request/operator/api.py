from las_rest.core.api import LasTopApi
from las_rest.utils.tool import update_dict

LIST_OPERATORS = "ListOperators"
LIST_OPERATOR_NAMES = "ListOperatorNames"
CREATE_OPERATOR = "CreateOperator"
GET_OPERATOR = "GetOperator"
ALTER_OPERATOR = "AlterOperator"
DROP_OPERATOR = "DropOperator"
UPSERT_OPERATOR = "UpsertOperator"



class OperatorApi(LasTopApi):
    name = 'OperatorApi'

    def __init__(self, api_client, scheme="https", host="open.volcengineapi.com", service_name="las",
                 region="cn-beijing", version="2024-04-30", env="online"):
        super(OperatorApi, self).__init__(api_client, scheme=scheme, host=host, service_name=service_name,
                                          region=region,
                                          version=version, env=env)

    def get_operator(self, catalog_name, schema_name, operator_name):
        base_request_params = self.create_request_params(GET_OPERATOR)
        req_params = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "OperatorName": operator_name
        }, **base_request_params)
        response = self._call_get_method(req_params=req_params)
        return response

    def create_operator(self, catalog_name, schema_name, operator_name, run_env, provider,
                        location, code_file, parameters, comment=None, tags=None, input=None, output=None):
        req_params = self.create_request_params(CREATE_OPERATOR)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "OperatorName": operator_name,
            "RunEnv": run_env,
            "Provider": provider,
            "Location": location,
            "CodeFile": code_file,
            "Parameters": parameters,
        }
        update_dict(req_body,"Comment", comment)
        update_dict(req_body,"Tags", tags)
        update_dict(req_body,"Input", input)
        update_dict(req_body,"Output", output)
        response = self._call_post_method(req_params, req_body)
        return response

    def upsert_operator(self, catalog_name, schema_name, operator_name, run_env, provider,
                        location, code_file, parameters, comment=None, tags=None, input=None, output=None):
        req_params = self.create_request_params(UPSERT_OPERATOR)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "OperatorName": operator_name,
            "RunEnv": run_env,
            "Provider": provider,
            "Location": location,
            "CodeFile": code_file,
            "Parameters": parameters,
        }
        update_dict(req_body,"Comment", comment)
        update_dict(req_body,"Tags", tags)
        update_dict(req_body,"Input", input)
        update_dict(req_body,"Output", output)
        response = self._call_post_method(req_params, req_body)
        return response

    def alter_operator(self, catalog_name, schema_name, operator_name, run_env=None, provider=None,
                       location=None, code_file=None, parameters=None, comment=None, tags=None, input=None, output=None):
        req_params = self.create_request_params(ALTER_OPERATOR)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "OperatorName": operator_name
        }
        update_dict(req_body,"Comment", comment)
        update_dict(req_body,"Tags", tags)
        update_dict(req_body,"RunEnv", run_env)
        update_dict(req_body,"Provider", provider)
        update_dict(req_body,"Location", location)
        update_dict(req_body,"CodeFile", code_file)
        update_dict(req_body,"Parameters", parameters)
        update_dict(req_body,"Input", input)
        update_dict(req_body,"Output", output)
        response = self._call_post_method(req_params, req_body)
        return response

    def drop_operator(self, catalog_name, schema_name, operator_name):
        base_request_params = self.create_request_params(DROP_OPERATOR)
        req_body = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "OperatorName": operator_name
        }, **base_request_params)
        response = self._call_post_method(base_request_params, req_body)
        return response

    def list_operators(self, catalog_name, schema_name, operator_name=None, offset=1, limit=20):
        base_request_params = self.create_request_params(LIST_OPERATORS)
        req_params = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "Offset": offset,
            "Limit": limit
        }, **base_request_params)

        response = self._call_get_method(req_params=req_params)
        return response

    def list_operators_names(self, catalog_name, schema_name, operator_name=None, offset=1, limit=20):
        base_request_params = self.create_request_params(LIST_OPERATOR_NAMES)
        req_params = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "Offset": offset,
            "Limit": limit
        }, **base_request_params)
        update_dict(req_params,"OperatorName",operator_name)
        response = self._call_get_method(req_params=req_params)
        return response
