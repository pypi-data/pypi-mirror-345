from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class Auth(BaseAPI):

    @action("/open-api/auth/get-by-token")
    def get_by_token(self, temp_token, **kwargs) -> ApiResponse:
        """
        获取openKeyId和secretKey
        :param str temp_token: 卖家账号登录确认授权返回的tempToken
        :return:
        """
        data = {
            "tempToken": temp_token,
        }
        return self._request(data={**kwargs, **data})
