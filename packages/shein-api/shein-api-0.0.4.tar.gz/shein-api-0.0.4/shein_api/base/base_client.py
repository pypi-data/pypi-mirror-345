from json import JSONDecodeError

import shein_api.__version__ as vd
import logging
import time
from requests import request
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import get_random_key, get_signature, ShopType

log = logging.getLogger(__name__)

class BaseClient(object):
    method = 'GET'
    user_agent = f'python-shein-api-{vd}'

    def __init__( self, open_key, secret_key, shop_typ=ShopType, env='development', debug=False):
        self.open_key = open_key
        self.secret_key = secret_key

        if shop_typ in (ShopType.SELF_OPERATION, ShopType.SEMI_MANAGED):
            self.base_url = 'https://openapi.sheincorp.com'
        elif shop_typ in (ShopType.FULL_MANAGED, ShopType.SELF_OWNED, ShopType.OTHER):
            self.base_url = 'https://openapi.sheincorp.cn'

        if env == 'development':
            self.base_url = 'https://openapi-test01.sheincorp.cn'

        self.debug = debug
        self.headers = {
            'User-Agent': self.user_agent,
            "content-type": "application/json;charset=UTF-8",
            "x-lt-openKeyId": open_key
        }

    def generate_headers(self, api_path):
        timestamp = str(round(time.time() * 1000))
        random_key = get_random_key()
        signature = get_signature(self.open_key, self.secret_key, api_path, timestamp, random_key)
        headers = {**{
            "x-lt-timestamp": timestamp,
            "x-lt-signature": signature,
        }, **self.headers}
        if api_path == '/open-api/auth/get-by-token':
            headers.update({
                'x-lt-appid': self.open_key,
            })
        return headers

    def _api_url(self, api_path):
        return self.base_url + api_path

    def clean_data(self, data):
        if data is None:
            return {}
        elif isinstance(data, dict):
            # 递归清除value为None中的key
            return {k: self.clean_data(v) for k, v in data.items() if v is not None}
        else:
            return {k: v for k, v in data.items() if v is not None}

    def request(self, data: dict = None, params: dict = None) -> ApiResponse:

        data = self.clean_data(data)

        method = params.pop('method')
        path = params.pop('path')
        headers = self.generate_headers(path)
        if method in ('POST', 'PUT', 'PATCH'):
            res = request(method,
                          self._api_url(path),
                          params=params,
                          data=data,
                          headers=headers)
        else:
            res = request(method,
                          self._api_url(path),
                          params=params,
                          headers=headers)

        if self.debug:
            logging.info(headers or self.headers)
            logging.info(method + " " + self._api_url(path))
            if data is not None:
                logging.info(data)

        return self._check_response(res)

    def _check_response(self, res) -> ApiResponse:
        print(self.headers)
        if 200 <= res.status_code < 300:
            try:
                res.json() or {}
            except JSONDecodeError:
                js = {"status_code": res.status_code}
        else:
            try:
                js = res.json() or {}
            except JSONDecodeError:
                js = {}
        log.debug("Response before list handling: %s", js)
        return js
