#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Dict, Literal, Optional, Union


class BaseTag:
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get("key", ""),
            data.get("value", ""),
        )

    def __init__(self, key: str, value: Union[str, int] = ""):
        self.key = key
        self.value = value

    @property
    def dict(self):
        return {
            "key": self.key,
            "value": self.value,
        }

    def __repr__(self):
        attributes = []
        for unit, value in self.dict.items():
            if value != 0:
                attributes.append(f"{unit}={value}")
        return f"{self.__class__.__name__}({', '.join(attributes)})"

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.dict)

    def __eq__(self, other):
        if isinstance(other, BaseTag):
            return self.key == other.key and self.value == other.value
        if isinstance(other, dict):
            return self.key == other.get("key") and self.value == other.get("value")
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def update(
        self, key: Optional[str] = None, value: Optional[Union[str, int]] = None
    ):
        if key:
            self.key = key
        if value:
            self.value = value

    def export(self) -> Dict[str, any]:
        return {key: value for key, value in self.dict.items()}
