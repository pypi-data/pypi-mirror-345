from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class Finance(BaseAPI):

    @action("/open-api/finance/report-list")
    def report_list(self, page, per_page, add_time_end=None, add_time_start=None, last_update_time_end=None,
                    last_update_time_start=None, settlement_statuses=None,
                    **kwargs) -> ApiResponse:
        """
        报账单列表
        查询代运营模式账单列表，当前仅支持查询2024年1月1日至今的数据，需要查询更多数据需要在商家后台操作；
        :param (datetime, opt) add_time_end: 报账单生成时间结束值（北京时间）；格式：yyyy-MM-dd HH:mm:ss (报账单生成时间和最后更新时间任一必填，单次最多查询7天数据)
        :param (datetime, opt) add_time_start: 报账单生成时间开始值（北京时间）；格式：yyyy-MM-dd HH:mm:ss (报账单生成时间和最后更新时间任一必填，单次最多查询7天数据)
        :param (datetime, opt) last_update_time_end: 最后更新时间结束值（北京时间）；格式：yyyy-MM-dd HH:mm:ss (报账单生成时间和最后更新时间任一必填，单次最多查询7天数据)
        :param (datetime, opt) last_update_time_start: 最后更新时间开始值（北京时间）；格式：yyyy-MM-dd HH:mm:ss (报账单生成时间和最后更新时间任一必填，单次最多查询7天数据)
        :param int page: 页码
        :param int per_page: 每页大小，最大200
        :param ([int], opt) settlement_statuses: 结算状态；1：待确认/ 2：待结算/ 3：已结算/ 不传默认查所有
        :return:
        """
        data = {
            "addTimeEnd": add_time_end,
            "addTimeStart": add_time_start,
            "lastUpdateTime": last_update_time_end,
            "lastUpdateTimeStart": last_update_time_start,
            "page": page,
            "perPage": per_page,
            "settlementStatuses": settlement_statuses,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/finance/report-sales-detail")
    def report_sales_detail(self, query, per_page, report_order_no, **kwargs) -> ApiResponse:
        """
        报账单销售款收支明细
        该接口支持通过报账单号查询销售款明细数据
        :param (str, opt) query: 下一页数据查询的值
        :param int per_page: 每页大小，最大200
        :param str report_order_no: 报账单号
        :return:
        """
        data = {
            "query": query,
            "perPage": per_page,
            "reportOrderNo": report_order_no,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/finance/report-adjustment-detail")
    def report_adjustment_detail(self, query, per_page, report_order_no, **kwargs) -> ApiResponse:
        """
        报账单销售款收支明细
        该接口支持通过报账单号查询补扣款明细数据
        :param (str, opt) query: 下一页数据查询的值
        :param int per_page: 每页大小，最大200
        :param str report_order_no: 报账单号
        :return:
        """
        data = {
            "query": query,
            "perPage": per_page,
            "reportOrderNo": report_order_no,
        }
        return self._request(data={**kwargs, **data})
