from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class Mes(BaseAPI):

    @action("/open-api/mes/get-purchase-info")
    def get_purchase_info(self, accept_order_end_time = None, accept_order_start_time = None, factory_id_list = None,
                          produce_order_id_list = None, skc = None, **kwargs) -> ApiResponse:
        """
        MES-FAC-002 采购信息接口
        :param (str, opt) accept_order_end_time: 接单结束时间
        :param (str, opt) accept_order_start_time: 接单起始时间
        :param ([int], opt) factory_id_list: 工厂id集合
        :param ([int], opt) produce_order_id_list: 订单编号
        :param (str, opt) skc:sku
        :return:
        """
        data = {
            "acceptOrderEndTime": accept_order_end_time,
            "acceptOrderStartTime": accept_order_start_time,
            "factoryIdList": factory_id_list,
            "produceOrderIdList": produce_order_id_list,
            "skc": skc,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/get-material-info")
    def get_material_info(self, accept_order_end_time = None, accept_order_start_time = None, factory_id_list = None,
                          produce_order_id_list = None, skc = None, **kwargs) -> ApiResponse:
        """
        MES-FAC-003 领料信息接口
        :param (str, opt) accept_order_end_time: 接单结束时间
        :param (str, opt) accept_order_start_time: 接单起始时间
        :param ([int], opt) factory_id_list: 工厂id集合
        :param ([int], opt) produce_order_id_list: 订单编号
        :param (str, opt) skc:sku
        :return:
        """
        data = {
            "acceptOrderEndTime": accept_order_end_time,
            "acceptOrderStartTime": accept_order_start_time,
            "factoryIdList": factory_id_list,
            "produceOrderIdList": produce_order_id_list,
            "skc": skc,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/get-second-precess")
    def get_material_info(self, accept_order_end_time = None, accept_order_start_time = None, factory_id_list = None,
                          produce_order_id_list = None, skc = None, **kwargs) -> ApiResponse:
        """
        MES-FAC-004 二次工艺接口
        :param (str, opt) accept_order_end_time: 接单结束时间
        :param (str, opt) accept_order_start_time: 接单起始时间
        :param ([int], opt) factory_id_list: 工厂id集合
        :param ([int], opt) produce_order_id_list: 订单编号
        :param (str, opt) skc:sku
        :return:
        """
        data = {
            "acceptOrderEndTime": accept_order_end_time,
            "acceptOrderStartTime": accept_order_start_time,
            "factoryIdList": factory_id_list,
            "produceOrderIdList": produce_order_id_list,
            "skc": skc,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/get-big-goods-bom")
    def get_big_goods_bom(self, produce_order_idc = None, **kwargs) -> ApiResponse:
        """
        MES-FAC-005 大货bom接口
        :param (int, opt) produce_order_idc: 订单编号
        :return:
        """
        data = {
            "produceOrderId": produce_order_idc,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/bundle-info")
    def bundle_info(self, bundle_num = None, **kwargs) -> ApiResponse:
        """
        MES-FAC-005 大货bom接口
        :param (str, opt) bundle_num: 扎号
        :return:
        """
        data = {
            "bundleNum": bundle_num,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/material-anomalous/list")
    def material_anomalous_list(self, factory_ids = None, page_no=None, page_size=None, **kwargs) -> ApiResponse:
        """
        查询物料异常详细接口
        :param ([int], opt) factory_ids: 工厂权限
        :param (int, opt) page_no: 当前页数
        :param (int, opt) page_size: 每页数量
        :return:
        """
        data = {
            "factoryIds": factory_ids,
            "pageNo": page_no,
            "pageSize": page_size,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/purchase-detail-info-list")
    def purchase_detail_info_list(self, produce_order_id = None,  **kwargs) -> ApiResponse:
        """
        查询采购单详细接口
        :param ([int], opt) produce_order_id: 订单编号
        :return:
        """
        data = {
            "produceOrderId": produce_order_id,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/query-produce-order-ids")
    def query_produce_order_ids(self, end_time, start_time,  **kwargs) -> ApiResponse:
        """
        按时间查询生产制单号
        :param str end_time: 订单编号
        :param str start_time: 订单编号
        :return:
        """
        data = {
            "endTime": end_time,
            "startTime": start_time,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/deliver-order/list")
    def deliver_order_list(self, accept_order_end_time=None, accept_order_start_time=None, factory_id_list=None,
                           produce_order_id_list=None, skc=None, **kwargs) -> ApiResponse:
        """
        查询发货单信息
        :param (str, opt) accept_order_end_time: 接单结束时间
        :param (str, opt) accept_order_start_time: 接单起始时间
        :param ([int], opt) factory_id_list: 工厂id集合
        :param ([int], opt) produce_order_id_list: 订单编号
        :param (str, opt) skc: sku
        :return:
        """
        data = {
            "acceptOrderEndTime": accept_order_end_time,
            "acceptOrderStartTime": accept_order_start_time,
            "factoryIdList": factory_id_list,
            "produceOrderIdList": produce_order_id_list,
            "skc": skc,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/query-produce-order-info-by-id")
    def query_produce_order_info_by_id(self, produce_order_id, **kwargs) -> ApiResponse:
        """
        根据订单号查询订单信息
        :param int produce_order_id: 订单编号
        :return:
        """
        data = {
            "produceOrderId": produce_order_id,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/end-cut-bed")
    def end_cut_bed(self, **kwargs) -> ApiResponse:
        """
        裁床完成
        :return:
        """
        data = {
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/order-inventory-surplus/update")
    def order_inventory_surplus_update(self, **kwargs) -> ApiResponse:
        """
        更新供应商尾货
            {
                "produceOrderId": 11,
                "sizeInfo": {
                    "size": '尺码',
                    "quantity": 100, # 数量
                }
            }
        :return:
        """
        data = {

        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/get-order-info")
    def get_order_info(self, produce_order_id_list, accept_order_end_time = None, accept_order_start_time = None,
                       factory_id_list = None, skc = None, **kwargs) -> ApiResponse:
        """
        MES-FAC-001 订单数据获取接口
        :param [int] produce_order_id_list: 订单编号
        :param str accept_order_end_time: 接单结束时间
        :param str accept_order_start_time: 接单起始时间
        :param (int, opt) factory_id_list: 工厂id集合
        :param str skc: sku
        :return:
        """
        data = {
            "acceptOrderEndTime": accept_order_end_time,
            "acceptOrderStartTime": accept_order_start_time,
            "factoryIdList": factory_id_list,
            "produceOrderIdList": produce_order_id_list,
            "skc": skc,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/get-produce-order-info")
    def get_produce_order_info(self, produce_order_id,**kwargs) -> ApiResponse:
        """
        查询生产订单
        :param int produce_order_id: 订单编号
        :return:
        """
        data = {
            "produceOrderId": produce_order_id,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/mes/order-inventory-surplus/list")
    def order_inventory_surplus_list(self, factory_ids, page_no, page_size, **kwargs) -> ApiResponse:
        """
        查询供应商尾货
        :param ([int], opt) factory_ids: 订单编号
        :param (int, opt) page_no:当前页数
        :param (int, opt) page_size: 每页数量

        :return:
        """
        data = {
            "factoryIds": factory_ids,
            "pageNo": page_no,
            "pageSize": page_size,
        }
        return self._request(data={**kwargs, **data})
