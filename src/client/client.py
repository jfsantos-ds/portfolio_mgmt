"""
Client for the Portfolio Manager.
"""
from datetime import datetime as dt, timedelta as td
from getpass import getpass
from typing import Optional, Union

from degiroapi import DeGiro

from src.utils.enums import AssetType, TimeAggregation
from src.utils.util_funcs import get_window_start
from history import ClientHistory
from portfolio_item import PortfolioItem


class Client(DeGiro):

    def __init__(self, keep_pass: Optional[bool]=False) -> None:
        super().__init__()
        self._history = None
        self._password = None
        self._portfolio = None
        self._balance = None
        self._login(keep_pass)

    def _login(self, keep_pass: bool):
        MAX_TRIES = 3
        tries = 1
        auto = globals().get('AUTO_LOGIN', False)
        user = globals().get('USER', None)
        while True:
            try:
                print(f"LOGIN ATTEMPT #{tries}" + (" - " + user) if user and auto else None)
                if not auto:
                    user = input('Username: ')
                password = getpass()
                super().login(user, password)
                if keep_pass:
                    self._password = password
                    print("The password is being kept on the client session. Remember to close the client when you are done!")
            except Exception as e:
                print("\t"+e)
                tries+=1
                if tries<MAX_TRIES:
                    continue
                raise Exception("Max tries for login exceeded.")
            break

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, history):
        raise NotImplementedError

    @property
    def portfolio(self):
        return self._portfolio

    def get_balance(self, _print: bool=True) -> dict:
        "Returns cash funds of the account. Prints items by default, disable with '_print=False'."
        self._balance = self.getdata(AssetType.cash.value)
        if _print:
            print("Cashfunds:" , self._balance)
        return self._balance

    def get_portfolio(self) -> dict:
        "Returns products of the account portfolio. Prints items by default, disable with '_print=False'."
        products = self.getdata(AssetType.product.value, True)
        self._portfolio = [PortfolioItem(product, self) for product in products]
        return self._portfolio

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

    def get_history(self, cache_prefix: str='../../history/', store: bool=True, update: bool=True) -> dict:
        """Checks for the account history of the client id in a cache directory. Reads and returns in case it exists.
        Creates full history if non-existing.
        Updates, if incomplete as of date, when update is True.
        Stores or updates in disk if store is True."""
        # Search for history
        history_path = cache_prefix + self.username
        try:
            self.history = ClientHistory.load(cache_prefix)
        except:
            self.history = ClientHistory().compile(client)
            self.history.save(history_path)
        return self.history

    def _store_history(self):
        "Stores the ClientHistory object in the Encrypts the ClientHistory object using the session password"
        raise NotImplementedError


if __name__ == '__main__':
    USER = 'Jfsantos'
    AUTO_LOGIN = True
    client = Client(keep_pass=True)

    client.get_balance()

    portfolio = client.get_portfolio()
    for product in portfolio:
        print(product)

    #transactions = client.get_transactions()
    #print(transactions)
