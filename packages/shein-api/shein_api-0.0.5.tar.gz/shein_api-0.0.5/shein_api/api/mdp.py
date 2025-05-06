from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class Mdp(BaseAPI):

    @action("/open-api/mdp/get-order-info-list")
    def get_order_info_list(self, page_num, page_size, order_status, order_time_begin, order_time_end, **kwargs) -> ApiResponse:

        """ 获取大货订单信息
         :param int page_num:
         :param int page_size:
         :param int order_status: 1排产中；2产前确认中；3打印中；4转印中；5后整中；6烧花中；7待发货；8待收货；9已完成；10全部；
         :param str order_time_begin: 时间跨度最大30天
         :param str order_time_end: 时间跨度最大30天

         :return: 返回的 JSON 数据包
         """
        data = {
            "pageNum": page_num,
            "pageSize": page_size,
            "orderStatus": order_status,
            "orderTimeBegin": order_time_begin,
            "orderTimeEnd": order_time_end,
        }
        return self._request(data={**kwargs, **data})

    @action('/open-api/mdp/product/print-task/begin')
    def print_task_begin(self, order_no, design_style, final_material_sku, **kwargs) -> ApiResponse:

        """
        提供更新MDP打印任务开始
        :param (str, opt) order_no: 加工单号/异常单号/生产异常单号
        :param str design_style: 设计款号
        :param str final_material_sku: 成品sku
        :return:
        """
        data = {
            "orderNo": order_no,
            "designStyle": design_style,
            "finalMaterialSku": final_material_sku,
        }
        return self._request(data={**kwargs, **data})

    @action('/open-api/mdp/product/print-task/finish')
    def print_task_finish(self, order_no, design_style, final_material_sku, actual_print_num, **kwargs) -> ApiResponse:

        """
        提供更新MDP打印任务完成
        :param (str, optional) order_no: 加工单号/异常单号/生产异常单号
        :param str design_style: 设计款号
        :param str final_material_sku: 成品sku
        :param decimal actual_print_num: 实际打印米数
        :return:
        """
        data = {
            "orderNo": order_no,
            "designStyle": design_style,
            "finalMaterialSku": final_material_sku,
            "actualPrintNum": actual_print_num,
        }
        return self._request(data={**kwargs, **data})
