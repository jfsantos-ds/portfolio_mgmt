"""
Portfolio object definition
"""
from typing import List, Optional

from portfolio_mgmt.client.portfolio_item import PortfolioItem


class Portfolio(list):
    def __init__(self, portfolio_items: Optional[List[PortfolioItem]], client=None):
        super().__init__(portfolio_item for portfolio_item in portfolio_items)
        self.product_id_set = set([item.product.product_id for item in self])
        self.tickers = {item.product.symbol:item.product.ticker for item in self}
        self.client = client
        self.cash = None
        self.last_updated = None
