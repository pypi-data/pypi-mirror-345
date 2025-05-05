from datetime import datetime, timedelta
from typing import Dict, Literal, Optional, Union
import pytz

from pangu.particle.datestamp.datestamp import Datestamp
from pangu.particle.datestamp.time import Time
from pangu.particle.duration.duration import Duration


class Date(Datestamp):
    """
    A subclass of Datestamp that only represents a date (year, month, day).
    Time attributes are disabled, and adding/subtracting durations returns Date.

    """

    @classmethod
    def today(cls, time_zone_name=None) -> "Date":
        tz = pytz.timezone(time_zone_name or cls.TIME_ZONE_NAME)
        now = datetime.now(tz)
        return cls(now.year, now.month, now.day, time_zone_name)

    @classmethod
    def from_string(
        cls, string: str, date_format: str = None, time_zone_name: str = None
    ) -> "Date":
        tz = pytz.timezone(time_zone_name or cls.TIME_ZONE_NAME)
        fmt = date_format or cls.DATE_FORMAT
        dt = datetime.strptime(string, fmt).replace(tzinfo=tz)
        return cls(dt.year, dt.month, dt.day, time_zone_name)

    @classmethod
    def from_timestamp(cls, timestamp: float, time_zone_name: str = None) -> "Date":
        tz = pytz.timezone(time_zone_name or cls.TIME_ZONE_NAME)
        dt = datetime.fromtimestamp(timestamp, tz)
        return cls(dt.year, dt.month, dt.day, time_zone_name)

    def __init__(self, year, month, day, time_zone_name=None):
        super().__init__(year, month, day, 0, 0, 0, 0, time_zone_name)

    @property
    def attr(self) -> list:
        return [
            "year",
            "month",
            "day",
            "time_zone_name",
        ]

    def __add__(self, other):
        if isinstance(other, Duration):
            new_dt = self.datetime + timedelta(seconds=other.base)
            return Date(new_dt.year, new_dt.month, new_dt.day, self.time_zone_name)
        raise TypeError("Date can only be added with Duration")

    def __sub__(self, other):
        if isinstance(other, Duration):
            new_dt = self.datetime - timedelta(seconds=other.base)
            return Date(new_dt.year, new_dt.month, new_dt.day, self.time_zone_name)
        elif isinstance(other, Date):
            delta = self.datetime - other.datetime
            return Duration.from_timedelta(delta)
        raise TypeError("Date can only be subtracted with Duration or another Date")

    def combine(self, time: "Time") -> Datestamp:
        return Datestamp(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=time.hour,
            minute=time.minute,
            second=time.second,
            microsecond=time.microsecond,
            time_zone_name=self.time_zone_name,
        )

    def __repr__(self):
        attr_parts = []
        for key in self.attr:
            value = getattr(self, key, None)
            attr_parts.append(f"{key}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attr_parts)})"

    def __dir__(self):
        base = super().__dir__()
        return [
            item
            for item in base
            if item not in {"hour", "minute", "second", "microsecond"}
        ]

    def to_datestamp(
        self,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        time_zone_name=None,
    ) -> Datestamp:
        return Datestamp(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=microsecond,
            time_zone_name=time_zone_name or self.time_zone_name,
        )

    def export(self) -> Dict[str, Union[int, float]]:
        """
        Export datestamp object as a dictionary
        :return: dict: Dictionary representation of the datestamp

        """
        return {key: getattr(self, key, 0) for key in self.attr}
