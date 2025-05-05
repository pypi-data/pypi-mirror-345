#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Dict, Literal, Optional, Union
import hashlib

"""
	Loaded all hash algorithms from hashlib and created a
	dictionary with algorithm as key and hash object as value
"""
HASH_ALGORITHMS = {algo: hashlib.new(algo) for algo in hashlib.algorithms_available}
