from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class Warehouse(BaseAPI):

    @action("/open-api/msc/warehouse/list", method="GET")
    def warehouse_list(self, **kwargs) -> ApiResponse:
        """
        商家仓库列表查询(自主运营和半托管模式)
        功能介绍：查询商家仓库列表信息。适用应用：平台（自主运营）模式
        ⚠️注意：商家如果有多个仓库，修改库存时必须传仓库id
        :return:
        """
        return self._request(params={**kwargs})

    @action("/open-api/stock/stock-query")
    def stock_query(self, sku_code_list, skc_name_list, spu_name_list, warehouse_type, **kwargs) -> ApiResponse:
        """
        库存查询
        该API支持通过批量sku、skc、spu查询库存
        :param ([str], opt) sku_code_list: SHEIN生成SKU 最多传100个，skuCodeList/skcNameList/spuNameList ，请确保三个参数有且只有1个不为空；
        :param ([str], opt) skc_name_list: SHEIN生成SKC，skuCodeList/skcNameList/spuNameList ，请确保三个参数有且只有1个不为空；
        :param ([str], opt) spu_name_list: SHEIN生成SPU，skuCodeList/skcNameList/spuNameList ，请确保三个参数有且只有1个不为空；
        :param str warehouse_type: 仓库类型；1:查备货在SHEIN仓的库存/ 2:查半托管，自主运营模式的虚拟库存/ 3:查代运营（全托管）、SHEIN自营模式的虚拟库存
        :return:
        """
        data = {
            "skuCodeList": sku_code_list,
            "skcNameList": skc_name_list,
            "spuNameList": spu_name_list,
            "warehouseType": warehouse_type,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/gsp/goods/change-inventory")
    def change_inventory(self, sku_code, change_inventory_quantity=None, warehouse_code=None, sale_inventory=None,
                         **kwargs) -> ApiResponse:
        """
        库存查询
        该API支持通过批量sku、skc、spu查询库存
        :param (int, opt) change_inventory_quantity: 商品的总库存；changeInventoryQuantity和saleInventory入参为必填，且只能填写一个；
        :param str sku_code: SHEIN平台生成的SKU，仅限审核通过的SKU可以修改库存；审核失败的SKU不可用
        :param (str, opt) warehouse_code: 仓库id，如果店铺有多个仓库则必传。通过商家仓列表查询接口查看
        :param (int, opt) sale_inventory: 更新可售库存；可售库存=可用库存+临时锁库存（下单未付款数）；changeInventoryQuantity和saleInventory入参为必填，且只能填写一个；
        :return:
        """
        data = {
            "updateSkuInventoryQuantityRequests": {
                "changeInventoryQuantity": change_inventory_quantity,
                "saleInventory": sale_inventory,
                "skuCodeList": sku_code,
                "warehouseCodeList": warehouse_code,
            }
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/goods/stock-update")
    def stock_update(self, skc, shein_sku, available_number, stock_type, remark=None,
                     **kwargs) -> ApiResponse:
        """
        采购商库存更新(新)(仅代运营&自营模式)

        该API用于更新代运营（又称全托管、简易平台）和SHEIN自营商家的库存，接口支持全量方式更新；
        ⚠️注意：自主运营和半托管模式应用请勿使用；
        :param str skc: SHEIN平台生成的SKC，相当于商品发布的skc_name
        :param str shein_sku: SHEIN平台生成的SKU，相当于商品发布的skucode
        :param (str, opt) remark: 备注 不超过100个字符
        :param str available_number: 实际库存数量；
        :param str stock_type: 默认传3，全量覆盖
        :return:
        """
        data = {
            # 库存出入库信息 单次记录数不超过200条
            "stock": {
                "skc": skc,
                "shein_sku": shein_sku,
                "remark": remark,
                "available_number": available_number,
                "stock_type": stock_type,
            }
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/goods/query-sku-sales")
    def query_sku_sales(self, sku_code_list, **kwargs) -> ApiResponse:
        """
        根据SKU查询销量

        商家可以通过该接口查询7天和30天销量 平台限制的QPS为 40/S，某一时间点大批量的调用接口可能会导致限流
         接口的数据为每天北京时间0点统计更新，建议开发者在北京时间的凌晨2点到7点均匀的拉取数据
        :param str sku_code_list: skuCode，最多上传100个skuCode
        :return:
        """
        data = {
            "skuCodeList": sku_code_list,
        }
        return self._request(data={**kwargs, **data})
