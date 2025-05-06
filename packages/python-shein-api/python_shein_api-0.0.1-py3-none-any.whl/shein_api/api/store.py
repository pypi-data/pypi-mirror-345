from shein_api.api.base import BaseAPI
from shein_api.base.api_response import ApiResponse
from shein_api.base.helpers import action


class Store(BaseAPI):

    @action("/open-api/openapi-business-backend/query-store-info")
    def query_store_info(self, **kwargs) -> ApiResponse:
        """
        查询店铺信息
        该接口用于查询店铺信息，包括供应商id、店铺名称及商品发品额度等
        :return:
        """
        return self._request()
