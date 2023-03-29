"""
Client for the Portfolio Manager.
"""
from datetime import datetime as dt, timedelta as td
from typing import Optional, Union
import os
import pickle

import pandas as pd

from portfolio_mgmt.client.client_wrapper import DegiroClientWrapper
from portfolio_mgmt.client.portfolio import Portfolio
from portfolio_mgmt.client.portfolio_item import PortfolioItem
from portfolio_mgmt.client.product import Product
from portfolio_mgmt.utils.enums import TRANSACTIONS_COLUMNS, AssetType, TimeAggregation
from portfolio_mgmt.utils.util_funcs import get_window_start


class Client(DegiroClientWrapper):
    CACHE_DIR = "../cache"
    CACHE_NAME = "product_cache.pkl"

    def __init__(self) -> None:
        super().__init__()
        self._history = None
        self._portfolio = None
        self._balance = None
        self._user = None
        self._cache = None

        self._authenticated = False

    @property
    def portfolio(self):
        if not self._portfolio:
            self._portfolio = self._get_portfolio()
        return self._portfolio
    
    @property
    def cache(self):
        if not self._cache:
            self._cache = self.get_cache()
        return self._cache
    
    @classmethod
    def get_cache(cls, cache_name:str | None=None):
        cache_name = cls.CACHE_NAME if not cache_name else cache_name
        cache_path = os.path.join(cls.CACHE_DIR, cache_name)
        
        if not os.path.exists(cls.CACHE_DIR):
            os.makedirs(cls.CACHE_DIR)

        if os.path.isfile(cache_path):
            with open(cache_path, "rb") as f:
                cache = pickle.load(f)
        else:
            cache = {}
            
        return cache
    
    @classmethod
    def store_cache(cls, cache, cache_name:str | None=None):
        cache_name = cls.CACHE_NAME if not cache_name else cache_name
        cache_path = os.path.join(cls.CACHE_DIR, cache_name)
        with open(cache_path, 'wb') as f:
            pickle.dump(cache, f)

    def login(self, username, password, totp):
        if self._authenticated:
            print("Already logged in.")
        else:
            self.auth(username, password, totp)
            self._authenticated = True

    def get_balance(self, _print: bool = True) -> dict:
        "Returns cash funds of the account. Prints items by default, disable with '_print=False'."
        self._balance = self.getdata(AssetType.cash.value)
        if _print:
            print("Cashfunds:", self._balance)
        return self._balance

    def _get_portfolio(self) -> dict:
        """Gets the Portfolio of the account."""
        products = self.getdata(AssetType.product.value, filter_zero=True)
        portfolio = Portfolio([PortfolioItem(product, self) for product in products])
        return portfolio

    def get_orders(
        self,
        start: Optional[Union[dt, int]] = None,
        end: dt = dt.now(),
        group_by: Optional[TimeAggregation] = TimeAggregation.week,
        only_active: bool = True,
    ) -> dict:
        """Returns orders of the account in a time window.
        If start is not provided, define window where end is located according to 'group_by' (default weekly).
        Else if start is provided as an integer, define window going start days back from end.
        Else start can be provided as a datetime object to define the time interval precisely."""
        if not start:
            start = get_window_start(end, group_by)
        if isinstance(start, int):
            start = end - td(days=start)
            start = dt(start.year, start.month, start.day)
        assert start < end, "The provided time window is poorly defined, start is later than end mark."
        return self.orders(start, end, only_active)

    def get_transactions(
        self,
        start: Optional[Union[dt, int]] = None,
        end: dt = dt.now(),
        group_by: Optional[TimeAggregation] = TimeAggregation.week,
    ) -> pd.DataFrame:
        """Returns transactions of the account in a time window.
        If start is not provided, define window where end is located according to 'group_by' (default weekly).
        Else if start is provided as an integer, define window going start days back from end.
        Else start can be provided as a datetime object to define the time interval precisely."""
        if not start:
            start = get_window_start(end, group_by)
        elif isinstance(start, int):
            start = end - td(days=start)
            start = dt(start.year, start.month, start.day)
        assert start < end, "Time window poorly defined, end has to be later than start."
        transactions = self._transactions(
            start, end
        )  # Might need to map over bigger periods to circumvent API request horizon limits
        transactions = pd.DataFrame(transactions)
        transactions = transactions.astype({"productId": str})

        detailed_transactions: pd.DataFrame = self._join_product_info(transactions)
        detailed_transactions["date"] = pd.to_datetime(detailed_transactions.date)
        detailed_transactions.rename({"id": "transactionId"}, axis=1, inplace=True)
        detailed_transactions.rename({"orderTypeId": "orderType"}, axis=1, inplace=True)
        detailed_transactions = detailed_transactions[TRANSACTIONS_COLUMNS]
        detailed_transactions["orderType"] = detailed_transactions["orderType"].map(
            {0: "Limit", 1: "Stop Limit", 2: "Market"}
        )
        detailed_transactions.orderType.fillna("Other", inplace=True)
        detailed_transactions.set_index("transactionId", inplace=True)
        detailed_transactions.sort_index(ascending=False, inplace=True)
        return detailed_transactions

    def _join_product_info(self, transactions: pd.DataFrame):
        product_ids = set(transactions.productId.unique())
        portfolio_ids = self.portfolio.product_id_set.intersection(product_ids)
        missing_ids = product_ids.difference(portfolio_ids)

        product_list = [item.product.to_dict() for item in self.portfolio if item.product.product_id in portfolio_ids]
        for product_id in missing_ids:
            product_list.append(Product(product_id, self).to_dict())
        product_list = pd.DataFrame(product_list)

        detailed_transactions = transactions.merge(product_list, left_on="productId", right_on="product_id")
        return detailed_transactions
