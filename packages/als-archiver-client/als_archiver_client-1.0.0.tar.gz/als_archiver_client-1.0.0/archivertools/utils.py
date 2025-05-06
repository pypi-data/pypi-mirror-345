from datetime import datetime
import pytz

def to_UTC(datetime_obj: datetime, tznaive: bool) -> datetime:
    """
    Convert a datetime object to UTC.

    If the input is naive (i.e., lacks timezone info), it is assumed to be in US/Pacific time.
    The resulting UTC datetime can be returned as either timezone-aware or naive.

    Parameters:
    - datetime_obj (datetime): The datetime to convert.
    - tznaive (bool): If True, return a naive datetime (i.e., without tzinfo).

    Returns:
    - datetime: UTC datetime object (aware or naive depending on `tznaive`).
    """
    if datetime_obj.tzinfo is None:
        datetime_obj = datetime_obj.replace(tzinfo=pytz.timezone('US/Pacific'))
    datetime_obj = datetime_obj.astimezone(pytz.utc)
    if tznaive:
        datetime_obj = datetime_obj.replace(tzinfo=None)
    return datetime_obj


def to_PST(datetime_obj: datetime, tznaive: bool) -> datetime:
    """
    Convert a datetime object to US/Pacific time (PST/PDT).

    If the input is naive, it is assumed to be in UTC.
    The resulting PST datetime can be returned as either timezone-aware or naive.

    Parameters:
    - datetime_obj (datetime): The datetime to convert.
    - tznaive (bool): If True, return a naive datetime (i.e., without tzinfo).

    Returns:
    - datetime: PST datetime object (aware or naive depending on `tznaive`).
    """
    if datetime_obj.tzinfo is None:
        datetime_obj = datetime_obj.replace(tzinfo=pytz.utc)
    datetime_obj = datetime_obj.astimezone(pytz.timezone('US/Pacific'))
    if tznaive:
        datetime_obj = datetime_obj.replace(tzinfo=None)
    return datetime_obj
