"""
Financial product object definition
"""
from typing import Optional
from datetime import date

from yahooquery import Ticker
import pandas as pd

from portfolio_mgmt.client.client import Client
from portfolio_mgmt.utils.enums import CurrencyMapper
from portfolio_mgmt.utils.globals import DEFAULT_START_DATE

CURRENCYTYPEID = 311


class Product:
    history = {
        "start": None,  # First timestamp of the history data
        "end": None,  # Last timestamp of the history data
        "interval": None,  # Interval between each data point
        "data": None,
    }

    def __init__(self, id, client:Client | None=None):
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
        self.history = self.history.copy()
        if client:
            self._set_product(id, client)

    def get_history(self, symbol:str, start:date=DEFAULT_START_DATE, interval:str='1d'):
        def _update_history(history:dict) -> dict:
            _history = {}
            end = date.today()
            if _start:=history.get("start")!=start:
                older_history = ticker.history(start=start, end=_start, interval=interval).loc[symbol].reset_index(names="date")
                _history["data"] = pd.concat([older_history, history["data"]])
                _history["start"] = start
            if _end:=history.get("end")!=end:
                newer_history = ticker.history(start=_end, end=end, interval=interval).loc[symbol].reset_index(names="date")
                _history["data"] = pd.concat([history["data"], newer_history])
                _history["end"] = end
            return _history
        
        cache: dict[str, dict] = Client.get_cache()
        ticker = Ticker(symbol, validate=True)
        if (history:=cache.get(symbol, {})):
           _history = _update_history(history)
        else:
            _history = ticker.history(start=start, interval=interval
                                      ).loc[symbol].reset_index(names="date")
            history = {
                "start":start,
                "end":date.today(),
                "data":_history,
                "interval":interval,
            }
        if _history:
            cache[symbol] = history.update(_history)
            Client.store_cache(cache)
        return cache[symbol]        

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
