#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Dict, Literal, Optional, Union

from pangu.particle.constant.storage import BYTE
from pangu.particle.constant.storage import STORAGE_RATIO
from pangu.particle.constant.storage import STORAGE_UNIT_TABLE
from pangu.particle.constant.storage import LEGAL_STORAGE_UNITS


class Storage:
    def __init__(
        self,
        size: Optional[int] = 0,
        unit: LEGAL_STORAGE_UNITS = "b",
    ):
        self.size = size
        self.unit = unit

    @property
    def dict(self) -> Dict[str, Union[int, str]]:
        return {
            "size": self.size,
            "unit": self.unit,
        }

    @property
    def base(self) -> Union[int, float]:
        return self.get_base()

    def get_base(self) -> Union[int, float]:
        return self.size * STORAGE_UNIT_TABLE[self.unit] / STORAGE_UNIT_TABLE["b"]

    def __repr__(self) -> str:
        attributes = []
        for unit, value in self.dict.items():
            if value != 0:
                attributes.append(f"{unit}={value}")
        return f"{self.__class__.__name__}({', '.join(attributes)})"

    def __str__(self) -> str:
        return self.__repr__()

    # --- operators ---

    def __add__(self, other: "Storage"):
        if isinstance(other, Storage):
            return Storage(
                self.base + other.base,
                "b",
            ).to_unit(self.unit)
        if isinstance(other, (int, float)):
            return Storage(
                self.size + other,
                self.unit,
            )
        raise TypeError(
            f"unsupported operand type(s) for +: 'Storage' and '{type(other).__name__}'"
        )

    def __radd__(self, other: "Storage"):
        return self.__add__(other)

    def __eq__(self, other: "Storage"):
        if isinstance(other, Storage):
            return self.base == other.base
        if isinstance(other, (int, float)):
            return self.size == other
        return False

    def __sub__(self, other: "Storage"):
        if isinstance(other, Storage):
            return Storage(
                self.base - other.base,
                "b",
            ).to_unit(self.unit)
        if isinstance(other, (int, float)):
            return Storage(
                self.size - other,
                self.unit,
            )
        raise TypeError(
            f"unsupported operand type(s) for -: 'Storage' and '{type(other).__name__}'"
        )

    def __mul__(self, other: Union[int, float]):
        return Storage(
            self.size * other,
            self.unit,
        )

    def as_unit(self, unit: str = "b") -> "Storage":
        self.size = self.to_unit(unit).size
        self.unit = unit
        return self

    def to_unit(self, unit: str = "b") -> "Storage":
        new_size = self.size * STORAGE_UNIT_TABLE[self.unit] / STORAGE_UNIT_TABLE[unit]
        return Storage(new_size, unit)

    def get_readable_unit(self, threshold: float = 1.0) -> str:
        for unit in STORAGE_UNIT_TABLE:
            new_size = (
                self.size * STORAGE_UNIT_TABLE[self.unit] / STORAGE_UNIT_TABLE[unit]
            )
            if new_size >= threshold and new_size < 1024:
                return unit
        return self.unit

    def to_readable(self) -> "Storage":
        unit = self.get_readable_unit()
        return self.to_unit(unit)

    def as_readable(self) -> "Storage":
        readable = self.to_readable()
        self.size = readable.size
        self.unit = readable.unit
        return self

    def export(self) -> Dict[str, Union[any]]:
        return {
            key: value for key, value in self.dict.items() if value not in (None, set())
        }
