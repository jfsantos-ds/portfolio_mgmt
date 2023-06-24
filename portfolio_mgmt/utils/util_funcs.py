from datetime import datetime as dt, timedelta as td
import os

from pandas import DataFrame

from portfolio_mgmt.utils.enums import TimeAggregation


def get_window_start(datetime: dt, group_by: TimeAggregation) -> dt:
    datetime = dt(datetime.year, datetime.month, datetime.day)  # Use just year, month, day
    if group_by == TimeAggregation.year.value:
        return dt(datetime.year, 1, 1)
    elif group_by == TimeAggregation.quarter.value:
        quarter = (datetime.month - 1) // 3
        return dt(datetime.year, 1 + quarter * 3, 1)
    elif group_by == TimeAggregation.month.value:
        return dt(datetime.year, datetime.month, 1)
    elif group_by == TimeAggregation.week.value:
        return datetime - td(days=datetime.weekday())
    return datetime

def store_csv_to_temp_folder(df:DataFrame, name:str, temp_dir:str='cache'):
    os.makedirs(temp_dir, exist_ok=True)
    if not name.endswith('.csv'):
        name += '.csv'
    name = os.path.join(temp_dir, name)
    df.to_csv(name)