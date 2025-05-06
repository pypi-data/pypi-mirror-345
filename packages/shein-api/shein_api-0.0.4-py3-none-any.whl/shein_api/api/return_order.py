from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class ReturnOrder(BaseAPI):

    @action("/open-api/return-order/list")
    def return_order_list(self, query_type, start_time, end_time, page, page_size, return_order_status=None,
                         **kwargs) -> ApiResponse:
        """
        查询退货单列表
        通过该接口获取退货单列表；如何对接退货单请查看客单退货退款服务；
        :param int query_type: 时间查询的维度类型：1：退货单下发给到商家的时间/ 2：买家申请退货时间/ 3：退货单更新时间
        :param str start_time: yyyy-MM-dd HH:mm:ss 默认查询48小时以内数据
        :param str end_time: yyyy-MM-dd HH:mm:ss 默认查询48小时以内数据
        :param int page: 请求页码
        :param int page_size: limit【1，30】
        :param (int, opt) return_order_status: 1：已关闭/ 2：已申请/ 3：已取消/ 5：已收货/ 6：已妥投/ 7：待交接/ 8：待SHEIN仓中转/ 9：已完成
        :return:
        """
        data = {
            "queryType": query_type,
            "startTime": start_time,
            "endTime": end_time,
            "page": page,
            "pageSize": page_size,
            "returnOrderStatus": return_order_status,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/return-order/details")
    def return_order_details(self, return_order_no_list,
                                 **kwargs) -> ApiResponse:
        """
        退货单详情查询
        通过该接口获取退货单详情；如何对接退货单请查看客单退货退款服务；
        :param [str] return_order_no_list: 最多30条
        :return:
        """
        data = {
            "returnOrderNoList": return_order_no_list,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/return-order/sign-return-order")
    def sign_return_order(self, return_order_no, goods_id_list,
                                 **kwargs) -> ApiResponse:
        """
        退货单详情查询
        通过该接口获取退货单详情；如何对接退货单请查看客单退货退款服务；
        :param str return_order_no: 退货单号
        :param [int] goods_id_list: 签收的退货商品Id列表
        :return:
        """
        data = {
            "returnOrderNo": return_order_no,
            "goodsIdList": goods_id_list,
        }
        return self._request(data={**kwargs, **data})
