from datetime import datetime, timedelta
from typing import Dict, Literal, Optional, Union
import pytz

from pangu.particle.datestamp.datestamp import Datestamp
from pangu.particle.duration.duration import Duration


class Time(Datestamp):
    """
    A subclass of Datestamp that only represents a time (hour, minute, second).
    Date attributes are disabled, and adding/subtracting durations returns Time.

    """

    @classmethod
    def now(cls, time_zone_name=None) -> "Time":
        tz = pytz.timezone(time_zone_name or cls.TIME_ZONE_NAME)
        now = datetime.now(tz)
        return cls(now.hour, now.minute, now.second, now.microsecond, time_zone_name)

    @classmethod
    def from_string(
        cls, string: str, time_format: str = None, time_zone_name: str = None
    ) -> "Time":
        print("Using time_format:", time_format or cls.TIME_FORMAT)
        t = datetime.strptime(string, time_format or cls.TIME_FORMAT)
        return cls(t.hour, t.minute, t.second, t.microsecond, time_zone_name)

    @classmethod
    def from_timestamp(cls, timestamp: float, time_zone_name: str = None) -> "Time":
        dt = datetime.fromtimestamp(
            timestamp, pytz.timezone(time_zone_name or cls.TIME_ZONE_NAME)
        )
        return cls(dt.hour, dt.minute, dt.second, dt.microsecond, time_zone_name)

    def __init__(self, hour=0, minute=0, second=0, microsecond=0, time_zone_name=None):
        now = Datestamp.now(time_zone_name)
        super().__init__(
            now.year,
            now.month,
            now.day,
            hour,
            minute,
            second,
            microsecond,
            time_zone_name,
        )

    @property
    def attr(self) -> list:
        return [
            "hour",
            "minute",
            "second",
            "microsecond",
            "time_zone_name",
        ]

    def __add__(self, other):
        if isinstance(other, Duration):
            new_dt = self.datetime + timedelta(seconds=other.base)
            return Time(
                new_dt.hour,
                new_dt.minute,
                new_dt.second,
                new_dt.microsecond,
                self.time_zone_name,
            )
        raise TypeError("Time can only be added with Duration")

    def __sub__(self, other):
        if isinstance(other, Duration):
            new_dt = self.datetime - timedelta(seconds=other.base)
            return Time(
                new_dt.hour,
                new_dt.minute,
                new_dt.second,
                new_dt.microsecond,
                self.time_zone_name,
            )
        elif isinstance(other, Time):
            delta = self.datetime - other.datetime
            return Duration.from_timedelta(delta)
        raise TypeError("Time can only be subtracted with Duration or another Time")

    def __repr__(self):
        attr_parts = []
        for key in self.attr:
            if key in {"year", "month", "day"}:
                continue
            value = getattr(self, key, None)
            attr_parts.append(f"{key}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attr_parts)})"

    def __dir__(self):
        base = super().__dir__()
        return [item for item in base if item not in {"year", "month", "day"}]

    def to_datestamp(
        self, year=None, month=None, day=None, time_zone_name=None
    ) -> Datestamp:
        return Datestamp(
            year=year or self.year,
            month=month or self.month,
            day=day or self.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
            microsecond=self.microsecond,
            time_zone_name=time_zone_name or self.time_zone_name,
        )

    def export(self) -> Dict[str, Union[int, float]]:
        """
        Export datestamp object as a dictionary
        :return: dict: Dictionary representation of the datestamp

        """
        return {key: getattr(self, key, 0) for key in self.attr}
