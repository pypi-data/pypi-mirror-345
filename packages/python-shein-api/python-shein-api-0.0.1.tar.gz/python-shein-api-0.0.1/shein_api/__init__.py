from . import api
from shein_api.base.base_client import BaseClient
from shein_api.base.helpers import ShopType


class SheinClient(BaseClient):

    def __init__(self, open_key, secret_key, shop_typ=ShopType, env='development', debug=False):
        super().__init__(open_key, secret_key, shop_typ, env, debug)
        self.auth = api.Auth(self)
        self.auth_service = api.AuthService(self)
        self.cargo = api.Cargo(self)
        self.feed = api.Feed(self)
        self.finance = api.Finance(self)
        self.goods = api.Goods(self)
        self.material = api.Material(self)
        self.mdp = api.Mdp(self)
        self.mes = api.Mes(self)
        self.order = api.Orders(self)
        self.return_order = api.ReturnOrder(self)
        self.shipping = api.Shipping(self)
        self.store = api.Store(self)
        self.warehouse = api.Warehouse(self)
