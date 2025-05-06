from typing import Dict, Any, List

from las_rest.core.api import LasTopApi

UPDATE_OPTIMIZER_TASK = "UpdateOptimizerTask"


class OptimizerApi(LasTopApi):
    name = 'OptimizerApi'

    def __init__(self, api_client, scheme="https", host="open.volcengineapi.com", service_name="las",
                 region="cn-beijing", version="2024-04-30", env="online"):
        super(OptimizerApi, self).__init__(api_client, scheme=scheme, host=host, service_name=service_name,
                                           region=region,
                                           version=version, env=env)

    def update_optimizer_task(self, catalog: str, database: str, table_name: str, type: str, taskId: int, task_detail: dict):
        base_request_params = self.create_request_params(UPDATE_OPTIMIZER_TASK)
        optimizer_task = dict({
            "CatalogName": catalog,
            "SchemaName": database,
            "TableName": table_name,
            "Type": type,
            "TaskId": taskId,
            "TaskDetail": task_detail
        })
        response = self._call_post_method(req_params=base_request_params, body=optimizer_task)
        return response
