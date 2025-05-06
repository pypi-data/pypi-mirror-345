from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class Orders(BaseAPI):

    @action("/open-api/order/order-list")
    def order_list(self, query_type, start_time, end_time, page, page_size, order_status=None, query_order_type=None,
                   cte_invoice_status=None, nfe_invoice_status=None, **kwargs) -> ApiResponse:
        """
        请求订单列表
        :param int query_type: 查询类型：1：根据订单下发时间查询/2：根据订单更新时间查询
        :param str start_time: 开始时间;示例：2024-12-12 15:38:29（UTC+8）
        :param str end_time: 结束时间;示例：2024-12-12 15:38:29（UTC+8）
        :param int page: 分页的页数
        :param int page_size: 每页返回的条数；请设置1～30的整数
        :param (int, opt) order_status: 订单状态：1：待处理/ 2：待发货/ 3：待shein发货/ 4：已发货/ 5：已签收/ 6：用户已退款/ 7：待shein揽收/ 8：已报损/ 9：已拒收
        :param (int, opt) query_order_type: 查询对应发货仓类型的订单；1:认证仓发货订单/ 2:SHEIN仓发货订单 / 3:商家仓发货订单/ 4: 所有订单
        :param (int, opt) cte_invoice_status: 巴西市场CTE开票状态（2025/05/13上线）；1:订单下所有包裹（取消的除外）已完成开票/ 2:订单下的包裹存在未完成开票
        :param (int, opt) nfe_invoice_status: 巴西市场NFE开票状态;1：已完成NFE开票/ 2：未完成NFE开票（对于巴西卖家，当订单发票信息通过回传发票信息同步后，状态从2变为1）/ 3：待重传NFE发票/ 4：无需开NFE发票
        :return:
        Returns:
            ApiResponse:
        """
        data = {
            "queryType": query_type,
            "startTime": start_time,
            "endTime": end_time,
            "page": page,
            "pageSize": page_size,
            "orderStatus": order_status,
            "queryOrderType": query_order_type,
            "cteInvoiceStatus": cte_invoice_status,
            "nfeInvoiceStatus": nfe_invoice_status,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/order/order-detail")
    def order_detail(self, order_no_list, **kwargs) -> ApiResponse:
        """
       请求订单列表
       :param [str] order_no_list: 订单号列表；最多30条；
       :return:
       Returns:
           ApiResponse:
       """
        data = {
            "orderNoList": order_no_list,
        }
        return self._request(data={**data, **kwargs})

    @action("/open-api/order/export-address")
    def export_address(self, order_no, handle_type, **kwargs) -> ApiResponse:
        """
          导出地址接口
          :param [str] order_no: 订单号
          :param int handle_type: 操作类型；1：仅导出收件人地址信息/ 2：导出收件人地址并将订单状态流转到待发货，即订单状态值从 "1" 更改为 "2"
          :return:
          Returns:
              ApiResponse:
        """
        data = {
            "orderNo": order_no,
            "handleType": handle_type,
        }
        return self._request(data={**data, **kwargs})

    @action("/open-api/order/express-channel")
    def export_channel(self, **kwargs) -> ApiResponse:
        """
          订单发货渠道查询
          :return:
          Returns:
              ApiResponse:
        """
        return self._request(data={**kwargs})

    @action("/open-api/order/import-batch-multiple-express")
    def import_batch_channel_express(self, **kwargs) -> ApiResponse:
        """
          批量上传运单号
          :return:
          Returns:
              ApiResponse:
        """
        return self._request(data={**kwargs})

    @action("/open-api/order/sync-invoice-info")
    def sync_invoice_info(self, **kwargs) -> ApiResponse:
        """
          回传发票信息 该接口用于巴西市场商家同步订单发票信息到 SHEIN平台
          :return:
          Returns:
              ApiResponse:
        """
        return self._request(data={**kwargs})

    @action("/open-api/order/print-express-info")
    def print_express_info(self, order_no, package_no, **kwargs) -> ApiResponse:
        """
          打印面单接口
          :param str order_no: 订单号
          :param [str] package_no: 包裹号；通过订单详情接口获取
          :return:
          Returns:
              ApiResponse:
        """
        data = {
            "orderNo": order_no,
            "packageNo": package_no,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/gsp/logistics-track", method="GET")
    def logistics_track(self, order_no=None, package_no=None, waybill_no=None, return_order_no=None, **kwargs) -> ApiResponse:
        """
          客单物流轨迹查询
          :param (str, opt) order_no: 正向订单号；正向订单号和退货单号必填一个；当查询正向订单号时，包裹号和运单号必填一个；
          :param (str, opt) package_no: 包裹号；包裹下有多运单的情况下会返回所有运单信息；
          :param (str, opt) waybill_no: 运单号；按指定运单号返回信息；
          :param (str, opt) return_order_no: 退货单号；
          :return:
          Returns:
              ApiResponse:
        """
        params = {
            "orderNo": order_no,
            "packageNo": package_no,
            "waybillNo": waybill_no,
            "returnOrderNo": return_order_no,
        }
        return self._request(params={**kwargs, **params})


    @action("/open-api/order/unpacking-group-confirm")
    def unpacking_group_confirm(self, order_no, **kwargs) -> ApiResponse:
        """
          确认超限拆分包裹
          :param str order_no: 订单号

          :return:
          Returns:
              ApiResponse:
        """
        data = {
            "orderNo": order_no,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/order/confirm-no-stock")
    def confirm_no_stock(self, order_no, sku_code, order_goods_id, **kwargs) -> ApiResponse:
        """
          确认无货接口
          :param str order_no: 订单号
          :param (str, opt) sku_code: SHEIN平台生成的 skuCode、skuCode 和 orderGoodsId 不允许同时为空
          :param (str, opt) order_goods_id: 商品唯一标识；同种商品多件，每件goodsId不同，通过订单详情接口获得
          :return:
          Returns:
              ApiResponse:
        """
        data = {
            "orderNo": order_no,
            "skuCode": sku_code,
            "orderGoodsId": order_goods_id,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/order/unpacking-group-remove")
    def unpacking_group_remove(self, order_no, **kwargs) -> ApiResponse:
        """
          取消超限拆分包裹
          :param str order_no: 订单号
          :return:
          Returns:
              ApiResponse:
        """
        data = {
            "orderNo": order_no,
        }
        return self._request(data={**kwargs, **data})
