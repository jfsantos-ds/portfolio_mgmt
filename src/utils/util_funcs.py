from datetime import datetime as dt, timedelta as td

from enums import TimeAggregation

def get_window_start(datetime: dt, group_by: TimeAggregation) -> dt:
    datetime = dt(datetime.year, datetime.month, datetime.day)  # Use just year, month, day
    if group_by == TimeAggregation.year:
        return dt(datetime.year, 1, 1)
    elif group_by == TimeAggregation.quarter:
        quarter = (datetime.month-1)//3
        return dt(datetime.year, 1 + quarter*3, 1)
    elif group_by == TimeAggregation.month:
        return dt(datetime.year, datetime.month, 1)
    elif group_by == TimeAggregation.week:
        return dt - td(days=dt.weekday())
    return datetime
