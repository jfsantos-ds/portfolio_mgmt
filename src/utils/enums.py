"Enums of the package"
from enum import Enum

from degiroapi.datatypes import Data

class AssetType(Enum):
    cash = Data.Type.CASHFUNDS
    product = Data.Type.PORTFOLIO

class TimeAggregation(Enum):
    day = 
    week = 
    month = 
    quarter = 
    year = 