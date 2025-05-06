from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class Shipping(BaseAPI):

    @action("/open-api/order/purchase-order-infos", method="GET")
    def purchase_order_infos(self, **kwargs) -> ApiResponse:
        """
        订单接口-获取采购单信息
        通过该接口获取采购单列表以及采购单详细信息；该接口适用SHEIN自营，全托管（代运营）应用；
        :return:
        """
        data = {
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/order/get-mothe-child-orders", method="GET")
    def get_mothe_child_orders(self, order_nos, select_jit_mother, **kwargs) -> ApiResponse:
        """
        JIT母单及子单对应关系查询接口
        :param [str] order_nos: 采购单号，支持批量，一次最多请求200采购单号。
        :param int select_jit_mother: 1、是(表示要查询的是母单) ；2、否（表示要查询的是子单，包括合单）
        :return:
        """
        data = {
            "orderNos": order_nos,
            "selectJitMother": select_jit_mother,
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/shipping/basic", method="GET")
    def shipping_basic(self, order_type, address_id=None, **kwargs) -> ApiResponse:
        """
        发货基本信息查询接口
        通过该接口获取商家发货地址，发货仓，支持的发货方式，打包方式，车队，自行委托第三方的物流服务商信息；
        :param int order_type: 订单类型 1：急采 2：备货
        :param (int, opt) address_id: 不同的发货地址可匹配不同的快递物流 不选择发货地址某些物流公司无法匹配
        :return:
        """
        data = {
            "orderType": order_type,
            "addressId": address_id,
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/shipping/express-company-list-v2")
    def express_company_list_v2(self, **kwargs) -> ApiResponse:
        """
        物流产品查询
        通过该接口查询SHEIN集成物流的时效产品以及对应的物流公司
        :return:
        """
        data = {
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/shipping/warehouse", method="GET")
    def shipping_warehouse(self, address_id, order_type, send_type, coding=None,
                           express_mode=None, order_no_list=None, **kwargs) -> ApiResponse:
        """
        收货仓信息查询
        通过该接口获取备货单的平台收货仓地址信息（适用全托管、SHEIN自营模式）；
        :param int address_id: 从发货基本信息查询接口获取；
        :param int order_type: 订单类型；1:急采；2：备货
        :param int send_type: 发货方式；1：快递物流；2：送货上门
        :param (str, opt) coding: 车队编码
        :param (str, opt) express_mode: 快递编码
        :param ([str], opt) order_no_list: 采购单号；建议填写，会影响地址的准确性；最多入参200个；
        :return:
        """
        data = {
            "orderType": order_type,
            "addressId": address_id,
            "sendType": send_type,
            "coding": coding,
            "expressMode": express_mode,
            "orderNoList": order_no_list,
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/shipping/orderToShipping")
    def order_to_shipping(self, **kwargs) -> ApiResponse:
        """
        创建发货单
        该接口为采购单生成发货单履约的场景调用。详细履约介绍请查看备货单履约管理文档。

        :return:
        """
        data = {

        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/shipping/modify-delivery-order-info")
    def modify_delivery_order_info(self, **kwargs) -> ApiResponse:
        """
        修改和取消发货单订单信息
        该接口主要用于：1、修改发货单订单包裹数量和商品数量；2、取消发货单订单；
        注意：箱唛和包裹类型的包裹数量入参不同，如需需求，请根据对应的入参设置。
        :return:
        """
        data = {
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/shipping/delivery/print-package")
    def print_package(self, delivery_no: str, **kwargs) -> ApiResponse:
        """
        发货单维度打印面单
        :param str delivery_no: 从发货基本信息查询接口获取；
        :return:
        """
        data = {
            "deliveryNo": delivery_no,
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/shipping/delivery", method="GET")
    def shipping_delivery(self, delivery_code = None, end_time = None, page = None, per_page = None, start_time = None, **kwargs) -> ApiResponse:
        """
        查询发货单列表
        :param str delivery_code: 从发货基本信息查询接口获取；
        :param str end_time: 根据发货单创建时间查询；日期格式 yyyy-MM-dd HH:mm:ss
        :param int page:
        :param int per_page: 最大200
        :param str start_time: 根据发货单创建时间查询；日期格式 yyyy-MM-dd HH:mm:ss
        :return:
        """
        data = {
            "deliveryCode": delivery_code,
            "endTime": end_time,
            "page": page,
            "perPage": per_page,
            "startTime": start_time,
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/ccst/v1/custom-info/queryAddCartInfo")
    def query_add_cart_info(self, custom_id, **kwargs) -> ApiResponse:
        """
        查询发货单列表
        :param str custom_id: 定制搭建ID；
        :return:
        """
        data = {
            "customId": custom_id,
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/ccst/v1/custom-infos")
    def custom_infos(self, custom_info_id, lang, **kwargs) -> ApiResponse:
        """
        获取定制数据 V1
        接口请求通讯成功统一返回 httpcode 200 返回body code错误码描述： 100001:CustomInfoId字段是为必填项
        100005:lang字段非法 120002:供应商ID不匹配 130002:该IP已达到1分钟60次限制
         120000:未找到CustomInfoId数据 100002:请求异常 9999:未知系统错误
        :param str custom_info_id: 定制搭建ID；
        :param str lang: 语种输入，影响label字段的语种输出；枚举：英语(美国) en_US , 德语 de_DE , 法语 fr_FR ,
         葡萄牙语(巴西) pt_BR , 西班牙语 es_ES , 日语 ja_JP , 意大利语 it_IT , 荷兰语 nl_NL , 繁体中文 zh_TW , 简体中文 zh_CN ,
          希伯来语(以色列) he_IL , 俄语 ru_RU , 阿拉伯语 ar_AR , 泰语 th_TH , 印度尼西亚语 id_ID , 土耳其语 tr_TR , 越南语 vi_VI ,
           瑞典语 sv_SV , 波兰语 pl_PL , 葡萄牙语 pt_PT , 韩语 ko_KR , 希腊语 el_GR , 捷克语 cs_CZ , 罗马尼亚语 ro_RO ,
            斯洛伐克语 sk_SK , 匈牙利语 hu_HU , 保加利亚语 bg_BG
        :return:
        """
        data = {
           "customInfoId": custom_info_id,
            "lang": lang,
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/ccst/v1/custom-info/templates")
    def custom_infos_templates(self, custom_info_id, need_update=None, **kwargs) -> ApiResponse:
        """
        获取模版数据V1
       接口请求通讯成功统一返回 httpcode 200 返回body code错误码描述：
        100001:CustomInfoId字段是为必填项 120001:未找到模版数据 120002:供应商ID不匹配 130002:该IP已达到1分钟60次限制
         100002:请求异常 9999:未知系统错误
        :param str custom_info_id: 定制搭建ID；
        :param (str, opt) need_update: 是否使用更新后的值，如果传true则返回最新的值，传false则返回用户加购物车时的值。默认为false。
        :return:
        """
        data = {
            "customInfoId": custom_info_id,
            "needUpdate": need_update,
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/ccst/v1/composite/task")
    def composite_task(self, composite_id, custom_info_id, need_update=None, **kwargs) -> ApiResponse:
        """
        创建⽣产模板任务V1

        :param str composite_id: 订单模板ID⽤于合成⽣产图⽚
        :param str custom_info_id: 定制数据ID，用户定制数据的唯一标识符
        :param (bool, opt) need_update: 是否使用更新后的compositeId，如果传true则返回最新的值，传false则返回用户加购物车时的值。默认为false。
        :return:
        """
        data = {
            "compositeId": composite_id,
            "customInfoId": custom_info_id,
            "needUpdate": need_update,
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/ccst/v1/composite/queryTask")
    def composite_query_task(self, id, **kwargs) -> ApiResponse:
        """
        查询任务结果V1
        :param str id: 从接口/ccst/openapi/v1/composite/task中获取id
        :return:
        """
        data = {
            "id": id,
        }
        return self._request(params={**kwargs, **data})
