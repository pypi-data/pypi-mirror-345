import json

from las_rest.utils.signature import SignerV4


class LasTopApi(object):
    name = 'BaseApi'

    def __init__(self, api_client=None, scheme="https", host="open.volcengineapi.com", service_name="las",
                 region="cn-beijing", version="2024-04-30", env="online"):
        self.api_client = api_client
        self._scheme = scheme
        self._host = host
        self._service_name = service_name
        self._region = region
        self._version = version
        self._env = env

    def _gen_base_request(self, content_type='application/json'):
        base_url = self._scheme + "://" + self._host
        base_header = dict({
            "Content-Type": content_type
        })
        return base_url, base_header

    def _call_get_method(self, req_params):
        base_url, base_header = self._gen_base_request()
        # signature gen
        ak, sk, sts_token = self.api_client.get_credentials()
        base_header['Host'] = self._host
        SignerV4.sign(path='', method='GET', headers=base_header, post_params=[], body="", query=req_params,
                      ak=ak, sk=sk, sts_token=sts_token, service=self._service_name, region=self._region)
        return self.api_client.call_get_method(base_header, base_url, req_params)

    def _call_post_method(self, req_params, body=dict()):
        base_url, base_header = self._gen_base_request()
        ak, sk, sts_token = self.api_client.get_credentials()
        base_header['Host'] = self._host
        SignerV4.sign(path='', method='POST', headers=base_header, post_params=[], body=json.dumps(body),
                      query=req_params,
                      ak=ak, sk=sk, sts_token=sts_token, service=self._service_name, region=self._region)
        return self.api_client.call_post_method(base_header, base_url, req_params, body)

    def create_request_params(self, action: str):
        real_action = self.get_action(action)
        return {
            "Action": real_action,
            "Version": self._version
        }

    def get_action(self, action: str):
        if "online" == self._env:
            return action
        elif "testing" == self._env:
            return "Testing" + action
        elif "staging" == self._env:
            return 'Staging' + action
        else:
            return "Preview" + action

