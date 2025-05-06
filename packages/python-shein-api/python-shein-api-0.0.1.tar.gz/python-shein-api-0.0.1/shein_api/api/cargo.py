from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class Cargo(BaseAPI):

    @action("/open-api/cargo/express-website-message")
    def express_website_message(self, **kwargs) -> ApiResponse:
        """
        物流商网点回调接口
        更新： 2021-11-19 1）opType 非必填，由SHEIN后台校验是新增还是修改。
         2）如果province，city，region，detail这几个字段需要变更且字段要置为空了，请传“”这个字符串。字段值=null一律视为不修改。
        :return:
        """
        data = {
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/cargo/qc-outside-cancel-sf-express")
    def qc_outside_cancel_sf_express(self, express_no: str, box_no: [str], **kwargs) -> ApiResponse:
        """
        顺丰运单未揽收包裹明细回调接口
        顺丰运单未揽收包裹明细回调接口，通知SHEIN未揽收的包裹号明细及运单号
        :param str express_no: 运单号
        :param [str] box_no: 包裹号，支持多个
        :return:
        """
        data = {
            "expressNo": express_no,
            "boxNo": box_no,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/cargo/express-notify")
    def express_notify(self, express_no: str, customer_order_number: str,
                       operate_type: int, code: int, error_info: str= None, **kwargs) -> ApiResponse:
        """
        物流商接口-物流商运单回调
        物流商运单回调接口，用于物流商在生产运单成功，修改运单，删除运单回调给shein
        :param str express_no: 物流单号
        :param str customer_order_number: shenin 下单单号
        :param int operate_type: 操作类型 1 下单通知，2修改运单通知，3取消运单通知
        :param int code: 处理结果 1 成功，-1失败
        :param (str, opt) error_info: 错误信息描述
        :return:
        """
        data = {
            "expressNo": express_no,
            "customerOrderNumber": customer_order_number,
            "operateType": operate_type,
            "code": code,
            "errorInfo": error_info,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/order/express-infos", method="GET")
    def express_infos(self, **kwargs) -> ApiResponse:
        """
        物流接口-获取快递公司信息
        提供给供应商查询快递信息
        :return:
        """
        data = {}
        return self._request(params={**kwargs, **data})

    @action("/open-api/cargo/track-notify")
    def track_notify(self, **kwargs) -> ApiResponse:
        """
        物流商推送轨迹数据-统一接口
        物流商推送轨迹数据给到Shein的统一接口
        :return:
        """
        data = {}
        return self._request(data={**kwargs, **data})

    @action("/open-api/cargo/track-notify-trackingmore")
    def track_notify_trackingmore(self, **kwargs) -> ApiResponse:
        """
        物流商推送轨迹数据-trackingmore
        trackingmore物流商推送轨迹数据给到Shein [接口文档](https://www.51tracking.com/v3/api-index#webhook)
        :return:
        """
        data = {}
        return self._request(data={**kwargs, **data})

    @action("/open-api/cargo/quote-return")
    def quote_return(self, operate_type, tracking_numbers: [str], quote_attachment = None,
                     remark = None, **kwargs) -> ApiResponse:
        """
        上传结算异常举证
        该接口用于物流商上传运单号异常的举证信息，举证信息不超过500字符，相关附件最多上传10个文件。
        :param int operate_type: 操作类型，枚举值：3-结算举证
        :param [str] tracking_numbers: 运单号
        :param ([str], opt) quote_attachment: 附件，支持回传多个附件链接（最多不超个10个，每个附件大小不超过10M）链接对应文件的格式限制：jpg、jpeg、png、xlsx、xls、pdf、docx、doc、zip、txt
        :param (str, opt) remark: 备注，限制不超过500字符（备注和附件至少填一个）
        :return:
        """
        data = {
            "operateType": operate_type,
            "trackingNumbers": tracking_numbers,
            "quoteAttachment": quote_attachment,
            "remark": remark,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/cargo/timeout-cancel-reason-return")
    def timeout_cancel_reason_return(self, tracking_number, operate_type, operate_source = None,
                     reason_type = None, remark = None, url_list = None, **kwargs) -> ApiResponse:
        """
        揽收超时/取消运单原因回传
        :param str tracking_number: 运单号
        :param int operate_type: 操作类型 枚举值：1-揽收超时，2-取消运单
        :param (int, opt) operate_source: 操作来源 枚举值：1-用户操作、2-物流操作 仅操作类型=取消运单，才回传值，根据操作的角色判断回传（会存在app、小程序等的操作，根据角色判断回传）
        :param (int, opt) reason_type: 原因类型 枚举值：1-用户原因、2-物流原因
        :param (str, opt) remark: 备注 限制不超过500字符
        :param ([str], opt) url_list: 附件 文件URL，支持回传多个附件链接（最多不超个10个，每个附件大小不超过10M）链接对应文件的格式限制：jpg、jpeg、png
        :return:
        """
        data = {
            "trackingNumber": tracking_number,
            "operateType": operate_type,
            "operateSource": operate_source,
            "reasonType": reason_type,
            "remark": remark,
            "urlList": url_list,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/cargo/logistics-trajectory-callback")
    def logistics_trajectory_callback(self, **kwargs) -> ApiResponse:
        """
        【新】物流轨迹回调
        :return:
        """
        data = {

        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/cargo/weight-callback")
    def weight_callback(self, **kwargs) -> ApiResponse:
        """
        【新】物流重量回调
        :return:
        """
        data = {

        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/cargo/platenum-callback")
    def platenum_callback(self, batch_code, plate_num, express_code_list, plate_num_two=None,
                          estimated_arrive_storage_time=None, freight_car_type=None,
                          freight_car_departure_time=None, **kwargs) -> ApiResponse:
        """
        车牌信息回调
        :param str batch_code: 批次号
        :param str plate_num: 车牌号
        :param [str] express_code_list: 运单号集合
        :param (str, opt) plate_num_two: 车牌号2
        :param (datetime, opt) estimated_arrive_storage_time: 预计到仓时间
        :param (str, opt) freight_car_type: 车型
        :param (datetime, opt) freight_car_departure_time: 车辆发车时间
        :return:
        """
        data = {
            "batchCode": batch_code,
            "plateNum": plate_num,
            "expressCodeList": express_code_list,
            "plateNumTwo": plate_num_two,
            "estimatedArrivalStorageTime": estimated_arrive_storage_time,
            "freightCarType": freight_car_type,
            "freightCarDepartureTime": freight_car_departure_time
        }
        return self._request(data={**kwargs, **data})
