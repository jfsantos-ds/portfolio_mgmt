"""
Item existing in financial portfolio object definition
"""
from typing import Optional

from colorama import Fore
from product import Product


class PortfolioItem:
    PRINT_LEN = 30

    def __init__(self, portfolio_listing: Optional[dict], client=None):
        if portfolio_listing:
            product_id = portfolio_listing["id"]
        self.product: Product = Product(product_id, client)
        self.size = None
        self.price = None
        self.wavg_price = None
        self.value = None
        self.last_updated = None
        self.purchased = False
        self._set_item(portfolio_listing)

    def _set_item(self, portfolio_listing: dict):
        self.size = portfolio_listing.get("size")
        self.price = portfolio_listing.get("price")
        self.wavg_price = portfolio_listing.get("breakEvenPrice")  # Degiro calls it Break Even Price
        self.purchased = self.wavg_price == 0
        self.value = portfolio_listing.get("value")
        self.last_updated = None

    def __str__(self):
        if self.product.type == "currency":
            return f"{self.size} {self.product.currency}"
        if self.purchased:
            returns = self.price * self.size
        else:
            returns = self.price / self.wavg_price - 1
        returns_substring = (
            (Fore.GREEN + "+" if returns >= 0 else Fore.RED)
            + (f"{self.price:.2f}{self.product.currency}" if self.purchased else f"{returns:.1%}")
            + Fore.RESET
        )
        return f"{self.size} {self.product.name[:self.PRINT_LEN]} @ {self.wavg_price:.2f}{self.product.currency} / {self.price:.2f}{self.product.currency} {returns_substring}"
