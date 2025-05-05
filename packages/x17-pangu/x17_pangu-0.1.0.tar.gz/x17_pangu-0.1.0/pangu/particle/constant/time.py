#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Time unit constants in seconds and conversions

"""
from typing import Dict, Literal, Optional, Union

SECOND = 1
TIME_UNIT_TABLE = {
    "year": SECOND * 60 * 60 * 24 * 365,
    "month": SECOND * 60 * 60 * 24 * 30,
    "week": SECOND * 60 * 60 * 24 * 7,
    "day": SECOND * 60 * 60 * 24,
    "hour": SECOND * 60 * 60,
    "minute": SECOND * 60,
    "second": SECOND,
    "millisecond": SECOND / 1000,
    "microsecond": SECOND / (1000 * 1000),
    "nanosecond": SECOND / (1000 * 1000 * 1000),
}
TIME_UNIT_TABLE_INDEX = {
    "second": 0,
    "millisecond": -1,
    "microsecond": -2,
    "nanosecond": -3,
    "minute": 1,
    "hour": 2,
    "day": 3,
    "week": 4,
    "month": 5,
    "year": 6,
}
PRECISE_TIME_UNIT_TABLE = {
    "second": SECOND,
    "minute": SECOND * 60,
    "hour": SECOND * 60 * 60,
    "day": SECOND * 60 * 60 * 24,
    "week": SECOND * 60 * 60 * 24 * 7,
    "month": SECOND * 60 * 60 * 24 * 30.4375,
    "year": SECOND * 60 * 60 * 24 * 365.25,
    "millisecond": SECOND / 1000,
    "microsecond": SECOND / (1000 * 1000),
    "nanosecond": SECOND / (1000 * 1000 * 1000),
}

TIME_UNITS = list(TIME_UNIT_TABLE.keys())
LEGAL_TIME_UNITS = Literal[
    "second",
    "minute",
    "hour",
    "day",
    "week",
    "month",
    "year",
    "millisecond",
    "microsecond",
    "nanosecond",
]
