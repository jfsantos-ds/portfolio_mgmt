"""
Client for the Portfolio Manager.
"""
from datetime import datetime as dt, timedelta as td
from typing import Optional, Union

from degiroapi import DeGiro

from utils.enums import AssetType, TimeAggregation
from utils.util_funcs import get_window_start


class Client(DeGiro):

    def __init__(self) -> None:
        super().__init__()

    def get_balance(self, _print: bool=True) -> dict:
        "Returns cash funds of the account. Prints items by default, disable with '_print=False'."
        cashfunds = self.getdata(AssetType.cash)
        if _print:
            for data in cashfunds:
                print(data)
        return cashfunds

    def get_portfolio(self, _print: bool=True) -> dict:
        "Returns products of the account portfolio. Prints items by default, disable with '_print=False'."
        products = self.getdata(AssetType.product, True)
        if _print:
            for data in products:
                print(data)
        return products

    def get_transactions(self, start: Optional[Union[dt, int]]=None, end: dt=dt.now(),
                         group_by: Optional[TimeAggregation]=TimeAggregation.week):
        """Returns transactions of the account in a time window.
        If start is not provided, define window where end is located according to 'group_by'.        
        Else if start is provided as an integer, define window going start days back from end.
        Else start can be provided as a datetime object to define the time interval precisely."""
        if not start:
            start = get_window_start(end, group_by)
        if isinstance(start, int):
            start = end - td(days=start)
            start = dt(start.year, start.month, start.day)
        assert start < end, "The provided time window is poorly defined, start is later than end mark."
        return self.transactions(start, end)


if __name__ == '__main__':
    client = Client()
    client.login()