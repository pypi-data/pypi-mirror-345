from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class Goods(BaseAPI):

    @action("/open-api/goods/product/publishOrEdit")
    def publish_or_edit(self, **kwargs) -> ApiResponse:
        """
        link: https://open.sheincorp.com/documents/apidoc/detail/3001020
        商品发布/编辑
        该API支持新增商品或全量更新商品，商品提交成功后，SHEIN会进行审核，可通过商品审核通知API跟踪审核状态。
        对接前请根据应用类型查看对应解决方案：商品管理（平台、半托管）、商品信息管理（代运营）。
        :return:
        """
        return self._request(data={**kwargs})

    @action("/open-api/goods/query-document-state")
    def query_document_state(self, **kwargs) -> ApiResponse:
        """
        link: https://open.sheincorp.com/documents/apidoc/detail/3001020
        查询商品审核状态
        该API支持通过spu查询skc的审核状态，支持查询spu指定版本的审核状态；同时，平台也支持webhook消息通知的方式推送商品审核结果，具体可查看商品公文审核通知
        "spuList": [
            {
                "spuName": spu_name,
                "version": version,
            }
        ]
        :return:
        """
        return self._request(data={**kwargs})

    @action("/open-api/openapi-business-backend/product/query")
    def product_query(self, page_num=None, page_size=None, insert_time_end=None, insert_time_start=None,
                             update_time_end=None, update_time_start=None, **kwargs) -> ApiResponse:
        """
        商品列表接口
        该API支持查询已发布成功的商品列表数据，接口一次最多返回50000条数据。如果商家发布的商品数量超过50000条，请增加时间范围进行查询。
        :param (int, opt) page_num: 页面数量，默认：1
        :param (int, opt) page_size: 页面大小，默认：50
        :param (str, opt) insert_time_end: 商品上新的结束时间（商品首次审核通过），示例：2024-11-15 19:00:00
        :param (str, opt) insert_time_start: 商品上新的开始时间（商品首次审核通过）示例：2024-11-15 20:00:00
        :param (str, opt) update_time_end: 商品的更新结束时间（更新范围不仅是商品信息变动，包括系统内部更新时间）.示例：2024-11-15 19:00:00
        :param (str, opt) update_time_start: 商品的更新开始时间（更新范围不仅是商品信息变动，包括系统内部更新时间）.示例：2024-11-15 19:00:00
        :return:
        """
        data = {
            "pageNum": page_num,
            "pageSize": page_size,
            "insertTimeEnd": insert_time_end,
            "insertTimeStart": insert_time_start,
            "updateTimeEnd": update_time_end,
            "updateTimeStart": update_time_start,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/goods/spu-info")
    def spu_info(self, language_list: [str], spu_name: str, **kwargs) -> ApiResponse:
        """
        spu商品详情查询(新)
        该API支持通过spuName查询spu详细信息，会返回spu信息以及spu下skc、sku信息
        :param [str] language_list: 语种列表，最多5个；
        支持语种:英语:en 法语:fr 西班牙语:es 德语:de 中文简体:zh-cn 泰语:th 巴西葡语:pt-br
        :param str spu_name: spuName，spuName是SHEIN生成的系统编码
        :return:
        """
        data = {
            "languageList": language_list,
            "spuName": spu_name,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/goods/query-category-tree")
    def query_category_tree(self, **kwargs) -> ApiResponse:
        """
        店铺查商品末级分类
        该API支持查询店铺的商品末级分类信息，不同店铺，分类会有差异。
        :return:
        """
        return self._request(data={**kwargs})

    @action("/open-api/goods/query-attribute-template")
    def query_attribute_template(self, product_type_id_list: [int], **kwargs) -> ApiResponse:
        """
        店铺查可选属性
        该API支持查询店铺可用属性，由于平台规则可能会变更，如增加主销售属性，修改属性是否必填等，建议一周更新一次；属性包括：产品属性、
        主销售属性（skc）、次销售属性（sku）、尺码表属性，可查看SHEIN商品属性介绍了解详细信息
        :param [int] product_type_id_list: 类型id集合，单次调用最多支持10个类型id
        :return:
        """
        data = {
            "product_type_id_list": product_type_id_list,
        }
        return self._request(data={**kwargs, **data})


    @action("/open-api/goods/get-custom-attribute-permission-config")
    def get_custom_attribute_permission_config(self, category_id_list: [str], **kwargs) -> ApiResponse:
        """
        查询是否支持自定义属性值
        该API支持查询当前分类是否支持自定义属性值
        :param [int] category_id_list: 分类ID，最多支持200个
        :return:
        """
        data = {
            "category_id_list": category_id_list,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/goods/add-custom-attribute-value")
    def add_custom_attribute_value(self, **kwargs) -> ApiResponse:
        """
        添加自定义属性值
        该API支持添加自定义属性值，请确保接口最多允许添加10000个自定义属性值，超过此限制将无法添加，
        而且平台不支持删除属性值。因此ERP系统应尽量使用店铺已有的属性值，只有在必要时才添加自定义属性值
        :return:
        """
        return self._request(data={**kwargs})


    @action("/open-api/goods/query-publish-fill-in-standard")
    def query_publish_fill_in_standard(self, category_id, spu_name, **kwargs) -> ApiResponse:
        """
        商品发布字段规范（含默认语种）
        该API支持查询商品发布时字段填写的规范，具体如下：
        1、默认语种（default_language：用于商品标题和商品描述上传）
        2、查询发品是否要上传竞品链接和库存证明（reference_product_link和proof_of_stock）
        3、查询商品发布时是否要上传样品（sample_info）
        4、查询商品发布品牌是否必传（brand_code）
        5、查询商品的skc标题是否必传（skc_title）
        6、查询半托管和代运营发布商品默认币种（currency）
        7、查询商品是否支持sku和spu维度传图片（picture_config_list）
        8、查询商品是否要上传最小备货数量（minimum_stock_quantity）
        :param long category_id: 末级分类id；该入参可用于查询店铺是否支持sku或spu维度图片、是否需要填写样品信息，其它场景不需要传；
        :param str spu_name: spu_name，(spu_name是SHEIN生成的系统编码)；该入参仅用于查询店铺是否支持sku或spu维度图片，其它场景不需要传；
        :return:
        """
        data = {
            "category_id": category_id,
            "spu_name": spu_name,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/goods/image-category-suggestion")
    def image_category_suggestion(self, url, **kwargs) -> ApiResponse:
        """
        根据商品图片查询类目
        该API支持根据商品图片推荐末级分类
        :return:
        """
        data = {
            "url": url,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/goods/transform-pic")
    def transform_pic(self, image_type, original_url, **kwargs) -> ApiResponse:
        """
        图片链接转换
        该API支持将外部的图片地址转换成SHEIN可用的图片地址，转换图片入参有以下要求：
        1、方形图尺寸：900 x 900 px - 2200 x 2200px
        2、色块图尺寸：80 x 80 px
        3、主图/细节图宽 x 高尺寸：1340 x 1785 px
        4、主图/细节图支持等比例方图：900 - 2200 px
        5、大小≤3MB，格式JPG/JPEG/PNG
        详细要求可查看方案：API支持上传SPU和SKU维度图片
        :param int image_type: 图片类型(1:主图; 2:细节图; 5:方块图; 6:色块图; 7:详情图)
        :param str original_url: spu_name，图片地址
        :return:
        """
        data = {
            "image_type": image_type,
            "original_url": original_url,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/goods/upload-pic")
    def upload_pic(self, image_type, file, **kwargs) -> ApiResponse:
        """
        本地图片上传
        该API支持将图片文件转换成在线图片链接
        1、方形图尺寸：900 x 900 px - 2200 x 2200px
        2、色块图尺寸：80 x 80 px
        3、主图/细节图宽 x 高尺寸：1340 x 1785 px
        4、主图/细节图支持等比例方图：900 - 2200 px
        5、大小≤3MB，格式JPG/JPEG/PNG
        详细要求可查看方案：API支持上传SPU和SKU维度图片
        :param int image_type: 图片类型(1:主图; 2:细节图; 5:方块图; 6:色块图; 7:详情图)
        :param blob file: 图片文件
        :return:
        """
        data = {
            "image_type": image_type,
            "file": file,
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/goods/query-site-list")
    def query_site_list(self, **kwargs) -> ApiResponse:
        """
        查询店铺站点和币种信息（新）
        该API支持查询店铺售卖的站点和币种信息
        :return:
        """
        data = {

        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/goods/query-brand-list")
    def query_brand_list(self, **kwargs) -> ApiResponse:
        """
        店铺查品牌列表
        该API支持查询店铺可用的品牌信息，店铺品牌会变动，请定期更新。
        :return:
        """
        data = {

        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/openapi-business-backend/product/price/save")
    def product_price_save(self, **kwargs) -> ApiResponse:
        """
        更新商品售价
        该API支持更新商品的售价信息，调整价格会有价格审核机制，需要重点关注返回参数中的status，只有修改成功之后才能再次发起修改价格，
        如果返回参数status=2待审核，需通过webhook：商品涨价审批结果通知，拿到结果之后才能再次修改价格。
        :return:
        """
        data = {
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/goods/update-cost")
    def update_cost(self, **kwargs) -> ApiResponse:
        """
        更新供货价
        该API支持更新商品供货价信息。
        :return:
        """
        data = {
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/goods/modify-skc-shelf")
    def modify_skc_shelf(self, **kwargs) -> ApiResponse:
        """
        商品上下架
        该API支持根据SKC维度修改商品上下架状态。
        :return:
        """
        data = {
        }
        return self._request(data={**kwargs, **data})

    @action("/open-api/goods-brand/whole-brands", method="GET")
    def whole_brands(self, page_num, page_size, **kwargs) -> ApiResponse:
        """
        查询全量品牌信息
        该API支持全量查询品牌信息，建议分页查询，不同店铺，品牌会存在差异，建议使用店铺查品牌列表
        :return:
        """
        data = {
            "page_num": page_num,
            "page_size": page_size,
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods/print-barcode")
    def print_barcode(self, **kwargs) -> ApiResponse:
        """
        商品打印条码
        使用该API打印商品条码
        :return:
        """
        data = {

        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods/get-certificate-rule")
    def get_certificate_rule(self, **kwargs) -> ApiResponse:
        """
        查询商品证书要求和审核状态
        该API支持查询证书要求及证书信息
        :return:
        """
        data = {

        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods/certificate/get-all-certificate-type-list-v2")
    def get_all_certificate_type_list_v2(self, **kwargs) -> ApiResponse:
        """
        查询证书所需上传资料（新）
        该API支持查询全量证书所需的资料，用于让开发者了解上传证书所需要填写的信息，比如：检测机构、电池型号、产品型号、证书编号、证书生效时间、证书失效时间等信息
        :return:
        """
        data = {
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods/upload-certificate-file")
    def upload_certificate_file(self, file, **kwargs) -> ApiResponse:
        """
        上传证书文件
        该API支持将本地文件转成SHEIN要求的在线URL
        :param blob file: file；单个20M以内、格式为PDF/PNG/JPG/JPEG的文件上传
        :return:
        """
        data = {
            "file": file,
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods/save-or-update-certificate-pool")
    def save_or_update_certificate_pool(self, **kwargs) -> ApiResponse:
        """
        商品证书池创建/编辑
        该API支持创建或编辑商品证书池。当certificateDimension=1，说明该类型的证书需要绑定SKC，因此需要创建商品证书池。
        另外在创建商品证书池之后，开发者还需要调用绑定SKC接口来完成证书上传
        :return:
        """
        data = {
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods/save-or-update-supplier-certificate")
    def save_or_update_supplier_certificate(self, certificate_type_id: str, certificate_url: str,
                                            certificate_url_name: str, certificate_pool_id: int = None,
                                            **kwargs) -> ApiResponse:
        """
        店铺证书池创建/编辑
        该API支持创建或编辑店铺证书池。当certificateDimension=2时，说明该类型的证书为店铺维度的证书，不需要绑定SKC商品。因此，在创建店铺证书池后，即可完成店铺证书的上传
        :param (int, opt) certificate_pool_id: 证书池id, 传了此值则执行更新，不传默认是新增
        :param int certificate_type_id: 证书类型ID
        :param str certificate_url: file；证书文件地址
        :param str certificate_url_name: 	证书文件名
        :return:
        """
        data = {
            "certificatePoolId": certificate_pool_id,
            "certificateTypeId": certificate_type_id,
            "certificateUrl": certificate_url,
            "certificateUrlName": certificate_url_name,
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods/save-certificate-pool-skc-bind")
    def save_certificate_pool_skc_bind(self, **kwargs) -> ApiResponse:
        """
        SKC绑定商品证书池
        该API支持商品证书池与商品绑定（SKC维度）。当certificateDimension=1，说明该类型的证书需要绑定SKC，
        因此在创建商品证书池后，需要调用该接口完成证书上传。
        :return:
        """
        data = {
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods-quality/environmental-label-rule/material-quality-tree-v2", method="GET")
    def material_quality_tree_v2(self, **kwargs) -> ApiResponse:
        """
        获取全量环保耗材信息（新）
        商品若要打印环保标，需先通过此接口获取平台支持的环保材料信息。
        环保材料信息共有两层，材料类型 -> 具体材料。
        :return:
        """
        data = {
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods-quality/environmental-label-rule/material-quality-tree", method="GET")
    def material_quality_tree(self, **kwargs) -> ApiResponse:
        """
        获取全量耗材类型和耗材材质信息
        该API支持获取全量耗材类型和耗材材质
        :return:
        """
        data = {
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods-quality/environmental-label-rule/list")
    def environmental_label_rule_list(self, **kwargs) -> ApiResponse:
        """
        获取环保标配置规则
        该API支持获取环保标配置规则
        :return:
        """
        data = {
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods-quality/environmental-label-rule/print")
    def environmental_label_rule_print(self, **kwargs) -> ApiResponse:
        """
        获取环保标配置规则
        该API支持获取环保标配置规则
        :return:
        """
        data = {
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods-compliance/label-print")
    def label_print(self, **kwargs) -> ApiResponse:
        """
        打印合规标签
        此接口支持打印合规相关的标签，包括：环保标签、GPSR标签、GPSR和环保标结合的标签、商家自定义标签。打印不同标签会要求您您提供不同入参，
        基于入参信息，匹配出可打印的所有标签内容。打印规则的匹配结果可能是失败，也可能是一个规则对应多个标签。
        注意：如果需要打印含有GPSR信息的标签，需要商家先在商家后台维护欧盟责任人、制造商信息，并绑定SKC。
        若没有维护，打印出来的标签内容会为空。不同标签类型的图片示例参考文档
        :return:
        """
        data = {
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods/batch-skc-size")
    def batch_skc_size(self, data: [str], **kwargs) -> ApiResponse:
        """
        打印合规标签
        此接口支持打印合规相关的标签，包括：环保标签、GPSR标签、GPSR和环保标结合的标签、商家自定义标签。打印不同标签会要求您您提供不同入参，
        基于入参信息，匹配出可打印的所有标签内容。打印规则的匹配结果可能是失败，也可能是一个规则对应多个标签。
        注意：如果需要打印含有GPSR信息的标签，需要商家先在商家后台维护欧盟责任人、制造商信息，并绑定SKC。
        若没有维护，打印出来的标签内容会为空。不同标签类型的图片示例参考文档
        :param [str] data: 商品条码数组
        :return:
        """
        data = {
            "data": data
        }
        return self._request(params={**kwargs, **data})

    @action("/open-api/goods/number-list", method="GET")
    def number_list(self, page: int, per_page: int, type: int, **kwargs) -> ApiResponse:
        """
        商品接口-全量查询SKC/SKU/设计款号关系列表
        该API支持查询skc/设计款号等编码信息
        :param int page: 商品条码数组
        :param int per_page: 每页数据量，最大值为100
        :param int type: 编号查询类型枚举。1: skc，2: 设计款号design_code,推荐入参1,入参2部分场景可能数据不存在
        :return:
        """
        data = {
            "page": page,
            "per_page": per_page,
            "type": type,
        }
        return self._request(params={**kwargs, **data})