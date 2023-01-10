"""
Client for the Portfolio Manager.
"""
from datetime import datetime as dt, timedelta as td
from getpass import getpass
from typing import Optional, Union
import requests

from degiroapi import DeGiro, ClientInfo, datatypes
from portfolio import Portfolio
from portfolio_item import PortfolioItem

from portfolio_mgmt.utils.enums import AssetType, TimeAggregation
from portfolio_mgmt.utils.util_funcs import get_window_start


class Client(DeGiro):
    __LOGIN_URL = "https://trader.degiro.nl/login/secure/login/totp"

    def __init__(self, keep_pass: Optional[bool] = False) -> None:
        super().__init__()
        self._history = None
        self._password = None
        self._portfolio = None
        self._balance = None

        self.login(keep_pass)

    def __request(self, url, cookie=None, payload=None, headers={}, data=None, post_params=None, request_type=None,
                  error_message='An error occurred.'):
        if not request_type:
            request_type = self._DeGiro__GET_REQUEST

        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0'

        if request_type == self._DeGiro__DELETE_REQUEST:
            response = requests.delete(url, json=payload)
        elif request_type == self._DeGiro__GET_REQUEST and cookie:
            response = requests.get(url, headers=headers, cookies=cookie)
        elif request_type == self._DeGiro__GET_REQUEST:
            response = requests.get(url, headers=headers, params=payload)
        elif request_type == self._DeGiro__POST_REQUEST and headers and data:
            response = requests.post(url, headers=headers, params=payload, data=data)
        elif request_type == self._DeGiro__POST_REQUEST and post_params:
            response = requests.post(url, headers=headers, params=post_params, json=payload)
        elif request_type == self._DeGiro__POST_REQUEST:
            response = requests.post(url, headers=headers, json=payload)
        else:
            raise Exception(f'Unknown request type: {request_type}')

        if response.status_code == 200 or response.status_code == 201:
            try:
                return response.json()
            except:
                return "No data"
        else:
            raise Exception(f'{error_message} Response: {response.text}')
            
    def __auth(self, username, password, totp):
        login_payload = {
            'username': username,
            'password': password,
            'isPassCodeReset': False,
            'isRedirectToMobile': False,
            'oneTimePassword': totp
        }
        login_response = self.__request(self.__LOGIN_URL, None, login_payload, request_type=self._DeGiro__POST_REQUEST,
                                        error_message='Could not login.')
        self.session_id = login_response['sessionId']
        client_info_payload = {'sessionId': self.session_id}
        client_info_response = self.__request(self._DeGiro__CLIENT_INFO_URL, None, client_info_payload,
                                              error_message='Could not get client info.')
        self.client_info = ClientInfo(client_info_response['data'])

        cookie = {
            'JSESSIONID': self.session_id
        }

        client_token_response = self.__request(self._DeGiro__CONFIG_URL, cookie=cookie, request_type=self._DeGiro__GET_REQUEST,
                                               error_message='Could not get client config.')
        self.client_token = client_token_response['data']['clientId']

        return client_info_response

    def login(self, keep_pass: bool):
        MAX_TRIES = 3
        tries = 0
        auto = globals().get("AUTO_LOGIN", False)
        user = globals().get("USER", None)
        while True:
            try:
                print(f"LOGIN ATTEMPT #{tries}" + (" - " + user) if user and auto else None)
                if not auto:
                    user = input("Username: ")
                password = getpass()
                totp = input("Provide 2FA token:")
                self.__auth(user, password, totp)
                if keep_pass:
                    self._password = password
                    print(
                        "Your password is being kept on the client session. Remember to close the client when you are done!"
                    )
            except Exception as e:
                print(str(e))
                tries += 1
                if tries < MAX_TRIES:
                    continue
                raise Exception("Max tries for login exceeded.")
            break

    @property
    def portfolio(self):
        return self._portfolio

    def getdata(self, datatype, filter_zero=None):
        data_payload = {
            datatype: 0
        }

        if datatype == datatypes.Data.Type.CASHFUNDS:
            return self.filtercashfunds(
                self.__request(self._DeGiro__DATA_URL + str(self.client_info.account_id) + ';jsessionid=' + self.session_id,
                               None,
                               data_payload,
                               error_message='Could not get data'))
        elif datatype == datatypes.Data.Type.PORTFOLIO:
            return self.filterportfolio(
                self.__request(self._DeGiro__DATA_URL + str(self.client_info.account_id) + ';jsessionid=' + self.session_id,
                               None,
                               data_payload,
                               error_message='Could not get data'), filter_zero)
        else:
            return self.__request(
                self._DeGiro__DATA_URL + str(self.client_info.account_id) + ';jsessionid=' + self.session_id, None,
                data_payload,
                error_message='Could not get data')

    def get_balance(self, _print: bool = True) -> dict:
        "Returns cash funds of the account. Prints items by default, disable with '_print=False'."
        self._balance = self.getdata(AssetType.cash.value)
        if _print:
            print("Cashfunds:", self._balance)
        return self._balance

    def get_portfolio(self) -> dict:
        """Gets the Portfolio of the account."""
        products = self.getdata(AssetType.product.value, filter_zero=True)
        self._portfolio = Portfolio([PortfolioItem(product, self) for product in products])
        return self._portfolio

    def get_transactions(
        self,
        start: Optional[Union[dt, int]] = None,
        end: dt = dt.now(),
        group_by: Optional[TimeAggregation] = TimeAggregation.week,
    ) -> dict:
        """Returns transactions of the account in a time window.
        If start is not provided, define window where end is located according to 'group_by' (default weekly).
        Else if start is provided as an integer, define window going start days back from end.
        Else start can be provided as a datetime object to define the time interval precisely."""
        if not start:
            start = get_window_start(end, group_by)
        elif isinstance(start, int):
            start = end - td(days=start)
            start = dt(start.year, start.month, start.day)
        assert start < end, "The provided time window is poorly defined, start is later than end mark."
        return self._transactions(start, end)

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

    def _transactions(self, from_date, to_date, group_transactions=False):
        transactions_payload = {
            'fromDate': from_date.strftime('%d/%m/%Y'),
            'toDate': to_date.strftime('%d/%m/%Y'),
            'group_transactions_by_order': group_transactions,
            'intAccount': self.client_info.account_id,
            'sessionId': self.session_id
        }
        return self.__request(self._DeGiro__TRANSACTIONS_URL, None, transactions_payload,
                              error_message='Could not get transactions.')['data']


if __name__ == "__main__":
    USER = "Jfsantos"
    AUTO_LOGIN = True
    client = Client(keep_pass=True)

    client.get_balance()

    # portfolio = client.get_portfolio()
    # for product in portfolio:
    #    print(product)

    transactions = client.get_transactions()
    print(transactions)
