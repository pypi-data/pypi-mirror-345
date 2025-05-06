import requests
from retry import retry

from las_rest.core.exception import ApiException, ClientException

client_retry_times = 3
# next retry will start after ${client_retry_interval} seconds
client_retry_interval = 5
# backoff seconds
client_retry_backoff = 3


class ApiClient:

    def __init__(self, ak, sk=None, sts_token=None, request_timeout=60):
        self.auth = Auth(ak=ak, sk=sk, sts_token=sts_token)
        self.request_timeout = request_timeout

    @classmethod
    def ak_sk_mode(cls, ak, sk):
        return cls(ak=ak, sk=sk)

    @classmethod
    def assume_role_mode(cls, ak, sts_token):
        return cls(ak=ak, sts_token=sts_token)

    @retry(tries=3, delay=5, backoff=3)
    def call_get_method(self, headers, url, req_params):
        return self.execute_call('GET', headers, url, req_params, [])

    @retry(tries=3, delay=5, backoff=3)
    def call_post_method(self, headers, url, req_params, post_params):
        return self.execute_call('POST', headers, url, req_params, post_params)

    def execute_call(self, method, headers, url, req_params, post_params):
        print("prepare call " f"{url} with request params " + f"{req_params} and play load " + f"{post_params}")
        if method == 'GET':
            response = requests.get(url=url, params=req_params, headers=headers, timeout=self.request_timeout)
        elif method == 'POST':
            response = requests.post(url=url, params=req_params, json=post_params, headers=headers,
                                     timeout=self.request_timeout)
        else:
            raise ApiException(status=405, reason=f"{method} not support")
        result = response.json()
        print("result: " + f"{result}")
        return result

    def update_auth(self, new_auth):
        self.auth = new_auth

    def get_credentials(self):
        return self.auth.access_key, self.auth.secret_key, self.auth.session_token


class Auth:
    access_key = None

    secret_key = None

    assume_role = False

    session_token = None

    identity_id = None

    identity_type = None

    def __init__(self, ak, sk, sts_token=None, identity_id=None, identity_type=None):
        self.access_key = ak
        assert ak is not None
        if sk is not None:
            self.secret_key = sk
        if sts_token is not None:
            self.session_token = sts_token
            self.assume_role = True
        elif self.secret_key is None and self.session_token is None:
            raise ClientException("user credential must be set properly")


class Configuration:
    retry_times = 3

    retry_interval = 5

    def __init__(self, retry_times=3, retry_interval=5):
        if retry_times is not None:
            self.retry_times = retry_times
        if retry_interval is not None:
            self.retry_interval = retry_interval
