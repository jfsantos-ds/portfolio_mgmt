"""
Client for the Portfolio Manager.
"""
import json
from datetime import datetime as dt, timedelta as td
from getpass import getpass
from typing import Optional, Union

import pandas as pd
import requests
from degiroapi import ClientInfo, DeGiro, datatypes

from portfolio_mgmt.client.portfolio import Portfolio
from portfolio_mgmt.client.portfolio_item import PortfolioItem
from portfolio_mgmt.client.product import Product
from portfolio_mgmt.utils.enums import TRANSACTIONS_COLUMNS, AssetType, TimeAggregation
from portfolio_mgmt.utils.util_funcs import get_window_start


class Client(DeGiro):
    __LOGIN_URL = "https://trader.degiro.nl/login/secure/login/totp"

    def __init__(self) -> None:
        super().__init__()
        self._history = None
        self._portfolio = None
        self._balance = None
        self._user = None

        self._authenticated = False

    @property
    def portfolio(self):
        if not self._portfolio:
            self._portfolio = self._get_portfolio()
        return self._portfolio

    def __request(
        self,
        url,
        cookie=None,
        payload=None,
        headers={},
        data=None,
        post_params=None,
        request_type=None,
        error_message="An error occurred.",
    ):
        if not request_type:
            request_type = self._DeGiro__GET_REQUEST

        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"

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
            raise Exception(f"Unknown request type: {request_type}")

        if response.status_code == 200 or response.status_code == 201:
            try:
                return response.json()
            except:
                return "No data"
        else:
            raise Exception(f"{error_message} Response: {response.text}")

    def __auth(self, username, password, totp):
        login_payload = {
            "username": username,
            "password": password,
            "isPassCodeReset": False,
            "isRedirectToMobile": False,
            "oneTimePassword": totp,
        }
        login_response = self.__request(
            self.__LOGIN_URL,
            None,
            login_payload,
            request_type=self._DeGiro__POST_REQUEST,
            error_message="Could not login.",
        )
        self.session_id = login_response["sessionId"]
        client_info_payload = {"sessionId": self.session_id}
        client_info_response = self.__request(
            self._DeGiro__CLIENT_INFO_URL, None, client_info_payload, error_message="Could not get client info."
        )
        self.client_info = ClientInfo(client_info_response["data"])

        cookie = {"JSESSIONID": self.session_id}

        client_token_response = self.__request(
            self._DeGiro__CONFIG_URL,
            cookie=cookie,
            request_type=self._DeGiro__GET_REQUEST,
            error_message="Could not get client config.",
        )
        self.client_token = client_token_response["data"]["clientId"]

        self._user=username

    def login(self, username, password, totp):
        if self._authenticated:
            return
        
        try:
            self.__auth(username, password, totp)
            self._authenticated=True
        except Exception as e:
            raise Exception(f"Login failed:\n{str(e)}")

    def getdata(self, datatype, filter_zero=None):
        data_payload = {datatype: 0}

        if datatype == datatypes.Data.Type.CASHFUNDS:
            return self.filtercashfunds(
                self.__request(
                    self._DeGiro__DATA_URL + str(self.client_info.account_id) + ";jsessionid=" + self.session_id,
                    None,
                    data_payload,
                    error_message="Could not get data",
                )
            )
        elif datatype == datatypes.Data.Type.PORTFOLIO:
            return self.filterportfolio(
                self.__request(
                    self._DeGiro__DATA_URL + str(self.client_info.account_id) + ";jsessionid=" + self.session_id,
                    None,
                    data_payload,
                    error_message="Could not get data",
                ),
                filter_zero,
            )
        else:
            return self.__request(
                self._DeGiro__DATA_URL + str(self.client_info.account_id) + ";jsessionid=" + self.session_id,
                None,
                data_payload,
                error_message="Could not get data",
            )

    def product_info(self, product_id):
        product_info_payload = {"intAccount": self.client_info.account_id, "sessionId": self.session_id}
        return self.__request(
            self._DeGiro__PRODUCT_INFO_URL,
            None,
            product_info_payload,
            headers={"content-type": "application/json"},
            data=json.dumps([str(product_id)]),
            request_type=self._DeGiro__POST_REQUEST,
            error_message="Could not get product info.",
        )["data"][str(product_id)]

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

    def _transactions(self, from_date, to_date, group_transactions=False):
        transactions_payload = {
            "fromDate": from_date.strftime("%d/%m/%Y"),
            "toDate": to_date.strftime("%d/%m/%Y"),
            "group_transactions_by_order": group_transactions,
            "intAccount": self.client_info.account_id,
            "sessionId": self.session_id,
        }
        transactions = self.__request(
            self._DeGiro__TRANSACTIONS_URL, None, transactions_payload, error_message="Could not get transactions."
        )["data"]
        return transactions
