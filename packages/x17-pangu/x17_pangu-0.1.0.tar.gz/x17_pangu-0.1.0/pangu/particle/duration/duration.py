#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import timedelta
from typing import Dict, Literal, Optional, Union
import time

from dateutil.relativedelta import relativedelta

from pangu.particle.constant.time import (
    LEGAL_TIME_UNITS,
    PRECISE_TIME_UNIT_TABLE,
    TIME_UNIT_TABLE,
    TIME_UNIT_TABLE_INDEX,
)


class Duration:
    TIME_UNIT_TABLE = TIME_UNIT_TABLE
    TIME_UNIT_TABLE_INDEX = TIME_UNIT_TABLE_INDEX
    TIME_UNITS = list(TIME_UNIT_TABLE.keys())

    @classmethod
    def set_precise(cls) -> None:
        """
        设置 Duration 为精确模式
        考虑到闰年和月份的天数差异，精确模式下的时间单位表如下：
        - year: 365.25 days
        - month: 30.4375 days

        :return: None

        """
        cls.TIME_UNIT_TABLE = PRECISE_TIME_UNIT_TABLE

    @classmethod
    def from_dict(cls, dictionary: Dict[str, int]) -> "Duration":
        """
        从字典创建 Duration 实例。
        :param dictionary: 包含时间单位的字典
            - year: int
            - month: int
            - week: int
            - day: int
            - hour: int
            - minute: int
            - second: int
            - millisecond: int
            - microsecond: int
        :return: Duration 实例

        """
        return cls(**{key: dictionary.get(key, 0) for key in cls.TIME_UNITS})

    @classmethod
    def from_timedelta(
        cls,
        td: timedelta,
        normalise: bool = True,
    ) -> "Duration":
        """
        从 datetime.timedelta 创建 Duration 实例.
        注意: timedelta 不包含 year 或 month 信息.
        :param td: datetime.timedelta 对象
        :param normalise: 是否归一化

        :return: Duration 实例

        """
        if not isinstance(td, timedelta):
            raise TypeError("Expected a datetime.timedelta object")
        return cls(
            day=td.days or 0,
            second=td.seconds or 0,
            microsecond=td.microseconds or 0,
            normalize=normalise,
        )

    @classmethod
    def from_relativedelta(
        cls,
        rd: relativedelta,
        normalise: bool = True,
    ) -> "Duration":
        """
        从 dateutil.relativedelta 创建 Duration 实例.
        注意: relativedelta 不包含 week 信息.
        :param rd: dateutil.relativedelta 对象
        :param normalise: 是否归一化

        :return: Duration 实例

        """
        if not isinstance(rd, relativedelta):
            raise TypeError("Expected a dateutil.relativedelta object")
        return cls(
            year=rd.years or 0,
            month=rd.months or 0,
            day=rd.days or 0,
            hour=rd.hours or 0,
            minute=rd.minutes or 0,
            second=rd.seconds or 0,
            microsecond=rd.microseconds or 0,
            normalize=normalise,
        )

    def __init__(
        self,
        year: Optional[int] = 0,
        month: Optional[int] = 0,
        week: Optional[int] = 0,
        day: Optional[int] = 0,
        hour: Optional[int] = 0,
        minute: Optional[int] = 0,
        second: Optional[int] = 0,
        millisecond: Optional[int] = 0,
        microsecond: Optional[int] = 0,
        nanosecond: Optional[int] = 0,
        normalize: bool = True,
        normalize_mode: Literal["calendar", "strict", "flat"] = "calendar",
    ) -> None:
        """
        初始化 Duration 对象，支持指定单位的数值或具体的时间参数。
        :param value: 数值

        :attr base: 对象的总秒数

        """
        # Precise duration params
        self.year = year
        self.month = month
        self.week = week
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.millisecond = millisecond
        self.microsecond = microsecond
        self.nanosecond = nanosecond

        # Base attributes
        self.normalize = normalize
        self.normalize_mode = normalize_mode
        if self.normalize:
            self.as_normalize()

    @property
    def attr(self) -> list:
        return [
            "year",
            "month",
            "week",
            "day",
            "hour",
            "minute",
            "second",
            "millisecond",
            "microsecond",
            "nanosecond",
        ]

    @property
    def dict(self) -> Dict[str, int]:
        return {
            unit: getattr(self, unit) for unit in self.TIME_UNITS if hasattr(self, unit)
        }

    @property
    def base(self) -> Union[int, float]:
        """
        作为基础单位（秒）的属性
        :return: Duration 对象的总秒数
        """
        return self.get_base()

    def get_base(self) -> Union[int, float]:
        """
        返回所有单位转换为基础单位（秒）的总和。
        :return: Duration 对象的总秒数

        """
        return sum(
            getattr(self, unit) * factor
            for unit, factor in self.TIME_UNIT_TABLE.items()
            if hasattr(self, unit) and getattr(self, unit) != 0
        )

    def as_normalize(self) -> None:
        total_seconds = self.get_base()
        ordered_units = sorted(
            self.TIME_UNIT_TABLE.items(),
            key=lambda x: TIME_UNIT_TABLE_INDEX[x[0]],
        )[::-1]

        for unit, factor in ordered_units:
            if factor == 0:
                setattr(self, unit, 0)
                continue
            setattr(self, unit, int(total_seconds // factor))
            total_seconds %= factor

        if total_seconds > 0:
            setattr(self, "second", getattr(self, "second", 0) + total_seconds)

    def __repr__(self) -> str:
        attributes = []
        for unit, value in self.dict.items():
            if value != 0:
                attributes.append(f"{unit}={value}")
        return f"{self.__class__.__name__}({', '.join(attributes)})"

    def __str__(self) -> str:
        return self.__repr__()

    def __add__(
        self,
        other: Union["Duration", timedelta, relativedelta],
    ) -> "Duration":
        if isinstance(other, timedelta):
            other = Duration.from_timedelta(other, normalise=False)
        elif isinstance(other, relativedelta):
            other = Duration.from_relativedelta(other, normalise=False)
        elif not isinstance(other, Duration):
            return NotImplemented

        combined = {
            unit: getattr(self, unit, 0) + getattr(other, unit, 0)
            for unit in self.TIME_UNITS
        }
        return Duration(**combined)

    def __sub__(
        self,
        other: Union["Duration", timedelta, relativedelta],
    ) -> "Duration":
        if isinstance(other, timedelta):
            other = Duration.from_timedelta(other, normalise=False)
        elif isinstance(other, relativedelta):
            other = Duration.from_relativedelta(other, normalise=False)
        elif not isinstance(other, Duration):
            return NotImplemented

        combined = {
            unit: getattr(self, unit, 0) - getattr(other, unit, 0)
            for unit in self.TIME_UNITS
        }
        return Duration(**combined)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return all(
            getattr(self, unit, 0) == getattr(other, unit, 0)
            for unit in self.TIME_UNITS
        )

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return self.get_base() < other.get_base()

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return self.get_base() <= other.get_base()

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return self.get_base() > other.get_base()

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return self.get_base() >= other.get_base()

    def __radd__(
        self, other: Union["Duration", timedelta, relativedelta]
    ) -> "Duration":
        return self.__add__(other)

    def __mul__(self, factor: Union[int, float]) -> "Duration":
        if not isinstance(factor, (int, float)):
            return NotImplemented
        scaled = {unit: getattr(self, unit, 0) * factor for unit in self.TIME_UNITS}
        return Duration(**{k: int(v) for k, v in scaled.items()})

    def __truediv__(self, divisor: Union[int, float]) -> "Duration":
        if not isinstance(divisor, (int, float)) or divisor == 0:
            raise ValueError("Divisor must be a non-zero int or float")
        scaled = {unit: getattr(self, unit, 0) / divisor for unit in self.TIME_UNITS}
        return Duration(**{k: int(v) for k, v in scaled.items()})

    def __hash__(self) -> int:
        return hash(tuple(getattr(self, unit, 0) for unit in self.TIME_UNITS))

    def __bool__(self) -> bool:
        return self.get_base() != 0

    def describe(self, as_text=False) -> str:
        """
        返回 Duration 对象的描述（人类可读）
        例如: "1 year, 2 months, 3 days"

        :return: 描述字符串
        """
        if not as_text:
            return self.dict
        else:
            description = []
            for unit in self.TIME_UNITS:
                value = getattr(self, unit, 0)
                if value != 0:
                    label = unit if value == 1 else unit
                    description.append(f"{value} {label}")
            return ", ".join(description) if description else "0 second"

    def set(self, **kwargs) -> None:
        """
        设置 Duration 对象的属性
        :param kwargs: 属性字典
            - year: int
            - month: int
            - week: int
            - day: int
            - hour: int
            - minute: int
            - second: int
            - millisecond: int
            - microsecond: int

        """
        for key, value in kwargs.items():
            if key in self.TIME_UNITS and isinstance(value, (int, float)):
                setattr(self, key, value)
        if self.normalize:
            self.as_normalize()

    def export(self) -> Dict[str, Union[int, float, str]]:
        return {key: value for key, value in self.dict.items()}

    def wait(self) -> None:
        """
        等待指定的时间段
        :return: None

        """
        time.sleep(self.get_base())