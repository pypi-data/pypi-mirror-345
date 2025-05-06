from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class AuthService(BaseAPI):

    @action("/open-api/lsps-java/auth/entity-change")
    def entity_change(self,  **kwargs) -> ApiResponse:
        """
        link: https://open.sheincorp.com/documents/apidoc/detail/3000740
        认证仓调用-接收认证仓服务商仓库渠道变更接口
        认证仓同步物理仓库、渠道接口
        :return:
        """
        data = {
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/order/openapi/auth/order/express-upload")
    def express_upload(self,  **kwargs) -> ApiResponse:
        """
        认证仓调用-上传物流运单接口
        认证仓上传物流运单
        :return:
        """
        data = {
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/order/openapi/auth/order/outbound-result")
    def outbound_result(self,  **kwargs) -> ApiResponse:
        """
        认证仓调用-回调出库单创建结果接口
        认证仓回调出库单创建结果
        :return:
        """
        data = {
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/order/openapi/auth/order/outbound-cancel")
    def outbound_cancel(self, cancel_reason, shein_warehouse_serial_no, outbound_order_no, billno, remark=None,
                             **kwargs) -> ApiResponse:
        """
        认证仓调用-作废出库单接口
        认证仓作废出库单
        :return:
        """
        data = {
            "cancelReason": cancel_reason,
            "sheinWarehouseSerialNo": shein_warehouse_serial_no,
            "outboundOrderNo": outbound_order_no,
            "remark": remark,
            "billno": billno,
        }
        return self._request(data={**kwargs, **data})
