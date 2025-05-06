"""
author: Andrea Pollastro - apollastro@lbl.gov
date:   04/19/2023
Python version: 3.10.8
"""
from datetime import datetime
import pytz

def to_UTC(datetime_obj: datetime, tznaive: bool) -> datetime:
        """ Converts datetime object to UTC datetime object.

        Params:
        - datetime_obj, datetime.datetime: datetime object - if tznaive, it will be 
                                           considered as US/Pacific tz (without 
                                           affecting the timestamp)
        - tznaive, bool: returns a datetime object tznaive or not

        Returns:
        - datetime_obj, datetime.datetime: datetime input converted to UTC time
        """
        if datetime_obj.tzinfo is None:
            datetime_obj.replace(tzinfo=pytz.timezone('US/Pacific'))
        datetime_obj = datetime_obj.astimezone(pytz.utc)
        if tznaive:
            datetime_obj = datetime_obj.replace(tzinfo=None)

        return datetime_obj

def to_PST(datetime_obj: datetime, tznaive: bool) -> datetime:
        """ Converts datetime object to PST datetime object.

        Params:
        - datetime_obj, datetime.datetime: datetime object - if tznaive, it will be 
                                           considered as UTC tz (without 
                                           affecting the timestamp)
        - tznaive, bool: returns a datetime object tznaive or not

        Returns:
        - datetime_obj, datetime.datetime: datetime input converted to PST time
        """
        if datetime_obj.tzinfo is None:
            datetime_obj.replace(tzinfo=pytz.utc)
        datetime_obj = datetime_obj.astimezone(pytz.timezone('US/Pacific'))
        if tznaive:
            datetime_obj = datetime_obj.replace(tzinfo=None)

        return datetime_obj