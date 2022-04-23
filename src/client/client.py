"""
Client for the Portfolio Manager.
"""
from datetime import datetime as dt, timedelta as td
from getpass import getpass
from typing import Optional, Union

from degiroapi import DeGiro

from src.utils.enums import AssetType, TimeAggregation
from src.utils.util_funcs import get_window_start
from src.history


class Client(DeGiro):

    def __init__(self, username: str, password: str) -> None:
        super().__init__()
        self.login(username, password)

    def get_balance(self, _print: bool=True) -> dict:
        "Returns cash funds of the account. Prints items by default, disable with '_print=False'."
        cashfunds = self.getdata(AssetType.cash.value)
        if _print:
            print("Cashfunds:" , cashfunds)
        return cashfunds

    def get_portfolio(self, _print: bool=True) -> dict:
        "Returns products of the account portfolio. Prints items by default, disable with '_print=False'."
        products = self.getdata(AssetType.product.value, True)
        return products

    def get_transactions(self, start: Optional[Union[dt, int]]=None, end: dt=dt.now(),
                         group_by: Optional[TimeAggregation]=TimeAggregation.week) -> dict:
        """Returns transactions of the account in a time window.
        If start is not provided, define window where end is located according to 'group_by' (default weekly).
        Else if start is provided as an integer, define window going start days back from end.
        Else start can be provided as a datetime object to define the time interval precisely."""
        if not start:
            start = get_window_start(end, group_by)
        if isinstance(start, int):
            start = end - td(days=start)
            start = dt(start.year, start.month, start.day)
        assert start < end, "The provided time window is poorly defined, start is later than end mark."
        return self.transactions(start, end)

    def get_orders(self, start: Optional[Union[dt, int]]=None, end: dt=dt.now(),
                   group_by: Optional[TimeAggregation]=TimeAggregation.week, only_active: bool=True) -> dict:
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

    def get_history(self, cache_prefix: str='../../history/', autostore: bool=True, autoupdate:) -> dict:
        """Checks for the account history of the client id in a cache directory. Reads and returns in case it exists.
        Creates full history if non-existing.
        Updates, if incomplete as of date, when autoupdate is True.
        Stores or updates in disk if autostore is True."""

        

if __name__ == '__main__':
    max_tries = 3
    tries = 1
    AUTO_LOGIN = True
    while True:
        try:
            print(f"LOGIN ATTEMPT #{tries}")
            user = 'Jfsantos'
            if not AUTO_LOGIN:
                print('Username: ')
                user = input()
            client = Client(user, getpass())
        except Exception as e:
            print("\t"+e)
            tries+=1
            if tries<max_tries:
                continue
        break

    client.get_balance()

    client.get_portfolio()

    transactions = client.get_transactions()