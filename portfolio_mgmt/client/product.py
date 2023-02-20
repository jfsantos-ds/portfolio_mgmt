"""
Financial product object definition
"""
from typing import Optional

from yahooquery import Ticker

from portfolio_mgmt.utils.enums import CurrencyMapper

CURRENCYTYPEID = 311


class Product:
    def __init__(self, id, client=None):
        super().__init__
        self.product_id = None
        self.name = None
        self.isin = None
        self.symbol = None
        self.type = None
        self.currency = None
        self.ticker = None
        self.buyTypes = None
        self.sellTypes = None
        self.active = None
        if client:
            self._set_product(id, client)

    def _set_product(self, id, client):
        try:
            product = client.product_info(id)
        except Exception as e:
            print(f"Product {id} get failed: {e}")
        is_currency = product.get("productTypeId") == CURRENCYTYPEID
        self.product_id = product.get("id")
        self.name = product.get("name")
        self.isin = product.get("isin")
        self.symbol = product.get("symbol")
        self.type = "currency" if is_currency else product.get("productType")
        self.currency = product.get("currency")
        self.buyTypes = product.get("buyOrderTypes")
        self.sellTypes = product.get("sellOrderTypes")
        self.active = product.get("active")
        if is_currency:
            self.currency = self.product_id
        elif self.active and self.symbol:
            ticker = Ticker(self.symbol, validate=True)
            if ticker.symbols:
                self.ticker = ticker
        self.currency = CurrencyMapper.get(self.currency, self.currency)

    def to_dict(self, filter_keys: Optional[list[str]] = None) -> dict:
        d = self.__dict__
        if filter_keys:
            for key in filter_keys:
                d.pop(key, None)
        return d
