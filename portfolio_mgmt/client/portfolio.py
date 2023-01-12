"""
Portfolio object definition
"""
from typing import List, Optional

from colorama import Fore
from product import Product


class Portfolio(list):
    def __init__(self, items: Optional[List[Product]], client=None):
        super().__init__(item for item in items)
        self.client = client
        self.cash = None
        self.last_updated = None

    def get_history(self, cache_prefix: str = "../../history/", store: bool = True, update: bool = True) -> dict:
        """Checks for the account history of the client id in a cache directory. Reads and returns in case it exists.
        Creates full history if non-existing.
        Updates, if incomplete as of date, when update is True.
        Stores or updates in disk if store is True."""
        # Search for history
        history_path = cache_prefix + self.username
        try:
            self.history = Portfolio.load(cache_prefix)
        except:
            self.history = self.compile(client)
            self.history.save(history_path)
        return self.history

    def _set_item(self, portfolio_listing: dict):
        self.id = portfolio_listing.get("id")
        self.size = portfolio_listing.get("size")
        self.price = portfolio_listing.get("price")
        self.wavg_price = portfolio_listing.get("breakEvenPrice")  # Degiro calls it Break Even Price
        self.value = portfolio_listing.get("value")
        self.last_updated = None