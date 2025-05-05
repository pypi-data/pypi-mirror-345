#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import Dict, Literal, Optional, Union

import pytz

from pangu.particle.constant.timezone import (
    DEFUALT_TIME_ZONE,
    DEFUALT_TIME_ZONE_NAME,
    TIMEZONE_TABLE,
)
from pangu.particle.duration.duration import Duration


class Datestamp:
    TIME_ZONE_NAME = DEFUALT_TIME_ZONE_NAME
    TIME_ZONE = DEFUALT_TIME_ZONE
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"
    DATE_TIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

    # --- attribute methods ---

    @classmethod
    def reset(cls) -> None:
        cls.DATE_FORMAT = "%Y-%m-%d"
        cls.TIME_FORMAT = "%H:%M:%S"
        cls.DATE_TIME_FORMAT = f"{cls.DATE_FORMAT} {cls.TIME_FORMAT}"
        cls.TIME_ZONE_NAME = DEFUALT_TIME_ZONE_NAME
        cls.TIME_ZONE = DEFUALT_TIME_ZONE

    @classmethod
    def configure(
        cls,
        date_format: str = None,
        time_format: str = None,
        date_time_format: str = None,
        time_zone_name: str = None,
    ) -> None:
        """
        Set class variables
        :param date_format (str): Date format
        :param time_format (str): Time format
        :param date_time_format (str): Datetime format
        :param time_zone_name (pytz.timezone): Timezone
        :return: None

        """
        if date_format:
            cls.DATE_FORMAT = date_format
        if time_format:
            cls.TIME_FORMAT = time_format
        if date_time_format:
            cls.DATE_TIME_FORMAT = date_time_format
        if time_zone_name:
            cls.TIME_ZONE_NAME = time_zone_name
            cls.TIME_ZONE = pytz.timezone(time_zone_name)

    @classmethod
    def get_time_zone(cls) -> pytz.timezone:
        return cls.TIME_ZONE

    @classmethod
    def get_time_zone_name(cls) -> str:
        return cls.TIME_ZONE_NAME

    @classmethod
    def get_date_format(cls) -> str:
        return cls.DATE_FORMAT

    @classmethod
    def get_time_format(cls) -> str:
        return cls.TIME_FORMAT

    @classmethod
    def get_date_time_format(cls) -> str:
        return cls.DATE_TIME_FORMAT

    # --- create methods ---

    @classmethod
    def now(
        cls,
        time_zone_name: str = None,
    ) -> "Datestamp":
        """
        Get current datestamp
        returns: Datestamp: Current date and time

        """
        dt = datetime.now(
            pytz.timezone(time_zone_name or cls.TIME_ZONE_NAME),
        )
        return cls(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            microsecond=dt.microsecond,
            time_zone_name=time_zone_name or cls.TIME_ZONE_NAME,
        )

    @classmethod
    def from_datetime(
        cls,
        dt: datetime,
        time_zone_name: str = None,
    ) -> "Datestamp":
        """
        Create datestamp object from datetime
        returns: datestamp object

        """
        return cls(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            microsecond=dt.microsecond,
            time_zone_name=time_zone_name or cls.TIME_ZONE_NAME,
        )

    @classmethod
    def from_timestamp(
        cls,
        timestamp: float,
        time_zone_name: str = None,
    ) -> "Datestamp":
        """
        Create Datestamp from timestamp
        returns: Datestamp: Datestamp object

        """
        tz = pytz.timezone(time_zone_name or cls.TIME_ZONE_NAME)
        dt = datetime.fromtimestamp(timestamp, tz)
        return cls(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            microsecond=dt.microsecond,
            time_zone_name=time_zone_name or cls.TIME_ZONE_NAME,
        )

    @classmethod
    def from_string(
        cls,
        string,
        date_time_format=None,
        time_zone_name: str = None,
    ) -> "Datestamp":
        """
        Create Datestamp from string
        returns: Datestamp: Datestamp object

        """
        tz = pytz.timezone(time_zone_name or cls.TIME_ZONE_NAME)
        dt_format = date_time_format or cls.DATE_TIME_FORMAT
        dt = datetime.strptime(
            string,
            dt_format,
        )
        return cls(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            microsecond=dt.microsecond,
            time_zone_name=time_zone_name or cls.TIME_ZONE_NAME,
        )

    @classmethod
    def from_iso(cls, string: str, time_zone_name: str = None) -> "Datestamp":
        """
        Create Datestamp from ISO 8601 format string.
        Example: "2025-04-26T11:00:00"
        """
        return cls.from_string(
            string=string,
            date_time_format="%Y-%m-%dT%H:%M:%S",
            time_zone_name=time_zone_name,
        )

    @classmethod
    def from_dict(
        cls,
        dictionary: Dict[str, Union[int, str]],
    ) -> "Datestamp":
        """
        Create Datestamp from dictionary
        returns: Datestamp: Datestamp object

        """
        return cls(
            year=dictionary.get("year"),
            month=dictionary.get("month"),
            day=dictionary.get("day"),
            hour=dictionary.get("hour"),
            minute=dictionary.get("minute"),
            second=dictionary.get("second"),
            microsecond=dictionary.get("microsecond"),
            time_zone_name=dictionary.get("time_zone_name") or cls.TIME_ZONE_NAME,
        )

    def __init__(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = 0,
        minute: Optional[int] = 0,
        second: Optional[int] = 0,
        microsecond: Optional[int] = 0,
        time_zone_name: Optional[str] = None,
    ):
        """
        Initialize Datestamp with date and time components.
        Args:
            year (int): Year
            month (int): Month
            day (int): Day
            hour (int): Hour
            minute (int): Minute
            second (int): Second
            microsecond (int): Microsecond
            tzinfo (pytz.timezone): Timezone info

        """
        if year is None or month is None or day is None:
            raise ValueError("year, month, and day must be provided")

        self.time_zone_name = time_zone_name or DEFUALT_TIME_ZONE_NAME
        self.time_zone = pytz.timezone(self.time_zone_name)

        # --- Step 3: Default to now() if everything is None ---
        if all(v is None for v in [year, month, day]):
            self.datetime = datetime.now(self.time_zone)
        else:
            self.datetime = datetime(
                year=year,
                month=month,
                day=day,
                hour=hour or 0,
                minute=minute or 0,
                second=second or 0,
                microsecond=microsecond or 0,
                tzinfo=self.time_zone,
            )

        self.year = self.datetime.year
        self.month = self.datetime.month
        self.day = self.datetime.day
        self.hour = self.datetime.hour
        self.minute = self.datetime.minute
        self.second = self.datetime.second
        self.microsecond = self.datetime.microsecond

    @property
    def attr(self) -> list:
        return [
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
            "microsecond",
            "time_zone_name",
        ]

    @property
    def date_str(self, date_format: str = None) -> str:
        return self.datetime.strftime(date_format or self.DATE_FORMAT)

    @property
    def time_str(self, time_format: str = None) -> str:
        return self.datetime.strftime(time_format or self.TIME_FORMAT)

    @property
    def datestamp_str(self, date_time_format: str = None) -> str:
        return self.datetime.strftime(date_time_format or self.DATE_TIME_FORMAT)

    @property
    def dict(self) -> Dict[str, Union[int, str]]:
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second,
            "microsecond": self.microsecond,
            "time_zone_name": self.time_zone_name,
        }

    def __repr__(self):
        attr_parts = []
        for key in self.attr:
            value = getattr(self, key, None)
            attr_parts.append(f"{key}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attr_parts)})"

    def __str__(self):
        return self.datetime.strftime(self.DATE_TIME_FORMAT)

    # --- get and set methods ---

    def get_datetime(self) -> datetime:
        """
        Get datetime object
        returns: datetime: Datetime object

        """
        return self.datetime

    def get_timestamp(self) -> float:
        """
        Get timestamp
        returns: float: Timestamp

        """
        return self.datetime.timestamp()

    def set(self, **kwargs) -> None:
        """
        Set attributes
        :param kwargs: Attributes to set
        :return: None

        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"{key} is not a valid attribute")
        self.datetime = datetime(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
            microsecond=self.microsecond,
            tzinfo=self.time_zone,
        )

    # --- operator methods ---

    def __add__(self, other: "Duration") -> "Datestamp":
        if isinstance(other, Duration):
            new_datetime = self.datetime + timedelta(seconds=other.base)
            return Datestamp.from_datetime(new_datetime, self.time_zone_name)
        else:
            raise TypeError("Unsupported type for addition")

    def __radd__(self, other: "Duration") -> "Datestamp":
        if isinstance(other, Duration):
            new_datetime = self.datetime + timedelta(seconds=other.base)
            return Datestamp.from_datetime(new_datetime, self.time_zone_name)
        else:
            raise TypeError("Unsupported type for reverse addition")

    def __sub__(
        self, other: Union["Duration", "Datestamp"]
    ) -> Union["Datestamp", "Duration"]:
        if isinstance(other, Duration):
            new_datetime = self.datetime - timedelta(seconds=other.base)
            return Datestamp.from_datetime(new_datetime, self.time_zone_name)
        elif isinstance(other, Datestamp):
            delta = self.datetime - other.datetime
            return Duration.from_timedelta(delta)
        else:
            raise TypeError("Unsupported type for subtraction")

    def __rsub__(self, other: "Datestamp") -> "Duration":
        if isinstance(other, Datestamp):
            delta = self.datetime - other.datetime
            return Duration.from_timedelta(delta)
        else:
            raise TypeError("Unsupported type for reverse subtraction")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Datestamp):
            raise TypeError("Unsupported type for equality check")
        return self.datetime == other.datetime

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Datestamp):
            raise TypeError("Unsupported type for inequality check")
        return self.datetime != other.datetime

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Datestamp):
            raise TypeError("Unsupported type for less than check")
        return self.datetime < other.datetime

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Datestamp):
            raise TypeError("Unsupported type for less than or equal check")
        return self.datetime <= other.datetime

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Datestamp):
            raise TypeError("Unsupported type for greater than check")
        return self.datetime > other.datetime

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Datestamp):
            raise TypeError("Unsupported type for greater than or equal check")
        return self.datetime >= other.datetime

    def __hash__(self) -> int:
        return hash(tuple(self.dict.values()))

    def __bool__(self) -> bool:
        return any(getattr(self, key, 0) != 0 for key in self.attr)

    # --- other methods ---

    def describe(self, as_text=False) -> str:
        """
        Describe the datestamp
        :return: str: Description

        """
        if not as_text:
            return self.dict
        else:
            description = []
            for key in self.attr:
                value = getattr(self, key, 0)
                if value != 0:
                    label = key if value == 1 else key
                    description.append(f"{value} {label}")
            return ", ".join(description) if description else "0 second"

    def export(self) -> Dict[str, Union[int, float]]:
        """
        Export datestamp object as a dictionary
        
        """
        return {
            "datestamp": self.datestamp_str,
            "timezone": self.time_zone_name,
        }