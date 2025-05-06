from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class Material(BaseAPI):

    @action("/open-api/material/out-inventory")
    def out_inventory(self, number_code, out_num, **kwargs) -> ApiResponse:
        """
        供应商库存-出库同步接口
        出库同步接口注意： 1.请求参数的中文不能出现unicode编码 如：柯桥变成了 \u67ef\u6865 2.请求参数中不能含有特殊的符号如制表符，换行符
        :param str number_code: 条编码
        :param str out_num: 本次出库数量
        :return:
        """
        data = {
            "numberCode": number_code,
            "outNum": out_num,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/material/sales-order-deliver-info")
    def sales_order_deliver_info(self, **kwargs) -> ApiResponse:
        """
        link: https://open.sheincorp.com/documents/apidoc/detail/3000490
        供应商订单-发货信息
        :return:
        """
        return self._request(data={**kwargs})

    @action("/open-api/material/sync-inventory")
    def sync_inventory(self, **kwargs) -> ApiResponse:
        """
        供应商库存-库存同步接口
        库存同步接口注意： 1.请求参数的中文不能出现unicode编码 如：柯桥变成了 \u67ef\u6865 2.请求参数中不能含有特殊的符号如制表符，换行符 3.一次同步的数量不能超过100条数据
        :return:
        """
        return self._request(data={**kwargs})

    @action("/open-api/material/receive-cloth-report")
    def receive_cloth_report(self, **kwargs) -> ApiResponse:
        """
        供应商质检-验布报告
        :return:
        """
        return self._request(data={**kwargs})

    @action("/open-api/material/in-inventory")
    def in_inventory(self, **kwargs) -> ApiResponse:
        """
        供应商库存-入库同步接口
        :return:
        """
        return self._request(data={**kwargs})
