#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from typing import Dict, Literal, Optional, Union
import pytz  # type: ignore

"""
    Loaded all timezones from pytz and created a 
    dictionary with timezone as key and offset 
    in hours as value

"""
SAFE_TIME = datetime.now()
TIMEZONE_TABLE = {
    timezone: int(
        pytz.timezone(timezone)
        .localize(SAFE_TIME, is_dst=False)
        .utcoffset()
        .total_seconds()
        / 3600
    )
    for timezone in pytz.all_timezones
}
DEFUALT_TIME_ZONE_NAME = "Australia/Sydney"
DEFUALT_TIME_ZONE = pytz.timezone(DEFUALT_TIME_ZONE_NAME)
