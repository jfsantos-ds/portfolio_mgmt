"Enums of the package"
from enum import Enum
from typing import Optional

from degiroapi.datatypes import Data


class AssetType(Enum):
    cash = Data.Type.CASHFUNDS
    product = Data.Type.PORTFOLIO

class TimeAggregation(Enum):
    day = 'day'
    week = 'week'
    month = 'month'
    quarter = 'quarter'
    year = 'year'

class CurrencyMapper(Enum):
    FLATEX_EUR = '€'
    EUR = '€'
    GBX = '1/100£'
    USD = '$'

    def get(item: str, default: Optional[str] = None):
        if item in CurrencyMapper.__members__:
            return CurrencyMapper[item].value
        return default
