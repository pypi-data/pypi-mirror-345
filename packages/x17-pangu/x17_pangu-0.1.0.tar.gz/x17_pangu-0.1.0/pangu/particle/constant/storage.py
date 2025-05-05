#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Dict, Literal, Optional, Union

"""
	Storage unit constants in bytes and conversions
	Default unit = byte
	Defualt ratio = 1024

"""
BYTE = 1
STORAGE_RATIO = 1024
STORAGE_UNIT_TABLE = {
    "b": BYTE,
    "byte": BYTE,
    "kb": BYTE * STORAGE_RATIO,
    "kilobyte": BYTE * STORAGE_RATIO,
    "mb": BYTE * STORAGE_RATIO**2,
    "megabyte": BYTE * STORAGE_RATIO**2,
    "gb": BYTE * STORAGE_RATIO**3,
    "gigabyte": BYTE * STORAGE_RATIO**3,
    "tb": BYTE * STORAGE_RATIO**4,
    "terabyte": BYTE * STORAGE_RATIO**4,
    "pb": BYTE * STORAGE_RATIO**5,
    "petabyte": BYTE * STORAGE_RATIO**5,
}
LEGAL_STORAGE_UNITS = Literal[
    "b",
    "byte",
    "kb",
    "kilobyte",
    "mb",
    "megabyte",
    "gb",
    "gigabyte",
    "tb",
    "terabyte",
    "pb",
    "petabyte",
]
