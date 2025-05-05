#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Dict, Literal, Optional, Union, List
from pangu.particle.base.tag import BaseTag


class BaseTagSet:
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data)

    def __init__(self, data: dict = {}) -> None:
        self.set = data

    @property
    def dict(self):
        return self.set

    def __repr__(self):
        attributes = []
        for unit, value in self.dict.items():
            if value != 0:
                attributes.append(f"{unit}={value}")
        return f"{self.__class__.__name__}({', '.join(attributes)})"

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, key: str):
        return self.set.get(key, None)

    def __setitem__(self, key: str, value: Union[str, int]):
        self.set[key] = value

    def __delitem__(self, key: str):
        if key in self.set:
            del self.set[key]

    def __eq__(self, other):
        if isinstance(other, BaseTagSet):
            return self.set == other.set
        elif isinstance(other, dict):
            return self.set == other
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self.set)

    def list(
        self,
    ) -> List:
        return [{key: value} for key, value in self.set.items()]

    def list_tags(
        self,
    ) -> List:
        return [BaseTag.from_dict({key: value}) for key, value in self.set.items()]

    def update(
        self,
        key: Union[str, Dict[str, Union[str, int]]],
        value: Optional[Union[str, int]] = "",
    ):
        if isinstance(key, dict):
            for k, v in key.items():
                self.set[k] = v
        else:
            if key in self.set:
                self.set[key] = value
            else:
                self.insert(key, value)

    def insert(
        self, key: Union[str, Dict[str, Union[str, int]]], value: Union[str, int] = ""
    ):
        if isinstance(key, dict):
            for k, v in key.items():
                self.set[k] = v
        else:
            self.set[key] = value
        return self.set

    def find(self, key: str) -> Optional[Union[str, int]]:
        return self.set.get(key, None)

    def delete(self, key: str):
        if key in self.set:
            del self.set[key]
        return self.set

    def find_by_prefix(self, prefix: str) -> List[BaseTag]:
        return [
            BaseTag.from_dict({"key": k, "value": v})
            for k, v in self.set.items()
            if k.startswith(prefix)
        ]

    def find_by_fuzzy(self, keyword: str) -> List[BaseTag]:
        return [
            BaseTag.from_dict({"key": k, "value": v})
            for k, v in self.set.items()
            if keyword.lower() in k.lower() or keyword.lower() in str(v).lower()
        ]

    def export(self) -> Dict[str, any]:
        return {key: value for key, value in self.dict.items()}
