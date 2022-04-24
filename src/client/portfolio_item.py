"""
PortfolioItem object definition
"""
from typing import Optional

from product import Product

class PortfolioItem(Product):

    def __init__(self, portfolio_listing: Optional[dict], client=None):
        self.size = None
        self.price = None
        self.wavg_price = None
        self.value = None
        self.last_updated = None
        if portfolio_listing:
            id = portfolio_listing['id']
            super().__init__(id, client)
            self._set_item(portfolio_listing)

    def _set_item(self, portfolio_listing: dict):
        self.id = portfolio_listing.get('id')
        self.size = portfolio_listing.get('size')
        self.price = portfolio_listing.get('price')
        self.wavg_price = portfolio_listing.get('breakEvenPrice')  # Degiro calls it Break Even Price
        self.value = portfolio_listing.get('value')
        self.last_updated = None

    def __str__(self):
        if self.type=='currency':
            return f'{self.size} {self.id}'
        return f'{self.size} {self.name[:20]} @ {self.price}{self.currency}'
