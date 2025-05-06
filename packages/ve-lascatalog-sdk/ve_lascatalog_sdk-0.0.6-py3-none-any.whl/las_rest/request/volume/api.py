from las_rest.core.api import LasTopApi
from las_rest.utils.tool import update_dict

LIST_VOLUMES = "ListVolumes"
LIST_VOLUME_NAMES = "ListVolumeNames"
CREATE_VOLUME = "CreateVolume"
GET_VOLUME = "GetVolume"
ALTER_VOLUME = "AlterVolume"
DROP_VOLUME = "DropVolume"
GET_VOLUME_CREDENTIALS = "GetVolumeCredentials"


class VolumeApi(LasTopApi):
    name = 'VolumeApi'

    def __init__(self, api_client, scheme="https", host="open.volcengineapi.com", service_name="las",
                 region="cn-beijing", version="2024-04-30", env="online"):
        super(VolumeApi, self).__init__(api_client, scheme=scheme, host=host, service_name=service_name, region=region,
                                        version=version, env=env)

    def get_volume(self, catalog_name, schema_name, volume_name):
        base_request_params = self.create_request_params(GET_VOLUME)
        req_params = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "VolumeName": volume_name
        }, **base_request_params)
        response = self._call_get_method(req_params=req_params)
        return response

    def create_volume(self, catalog_name, schema_name, volume_name, comment, volume_type, location):
        req_params = self.create_request_params(CREATE_VOLUME)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "VolumeName": volume_name,
            "Location": location
        }
        update_dict(req_body, "Comment", comment)
        update_dict(req_body, "Type", volume_type)

        response = self._call_post_method(req_params, req_body)
        return response

    def alter_volume(self, catalog_name, schema_name, volume_name, comment, volume_type, location):
        req_params = self.create_request_params(ALTER_VOLUME)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "VolumeName": volume_name,
            "Comment": comment,
            "Type": volume_type,
            "Location": location
        }
        response = self._call_post_method(req_params, req_body)
        return response

    def drop_volume(self, catalog_name, schema_name, volume_name):
        base_request_params = self.create_request_params(DROP_VOLUME)
        req_body = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "VolumeName": volume_name
        }, **base_request_params)
        response = self._call_post_method(base_request_params, req_body)
        return response

    def list_volumes(self, catalog_name, schema_name, volume_name, offset, limit):
        base_request_params = self.create_request_params(LIST_VOLUMES)
        req_params = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name
        }, **base_request_params)

        update_dict(req_params, "VolumeName", volume_name)
        update_dict(req_params, "Offset", offset)
        update_dict(req_params, "Limit", limit)

        response = self._call_get_method(req_params=req_params)
        return response

    def list_volume_names(self, catalog_name, schema_name, volume_name, offset, limit):
        base_request_params = self.create_request_params(LIST_VOLUME_NAMES)
        req_params = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name
        }, **base_request_params)

        update_dict(req_params, "VolumeName", volume_name)
        update_dict(req_params, "Offset", offset)
        update_dict(req_params, "Limit", limit)

        response = self._call_get_method(req_params=req_params)
        return response

    def get_volume_credentials(self, catalog_name, schema_name, volume_name, action_name, role_name, durations_seconds):
        base_request_params = self.create_request_params(GET_VOLUME_CREDENTIALS)
        req_params = dict({
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "VolumeName": volume_name,
            "ActionName": action_name
        }, **base_request_params)

        update_dict(req_params, "RoleName", role_name)
        update_dict(req_params, "DurationsSeconds", durations_seconds)

        response = self._call_get_method(req_params=req_params)
        return response
