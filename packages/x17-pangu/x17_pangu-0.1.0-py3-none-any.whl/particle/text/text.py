#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Dict, Literal, Optional, Union
from pangu.particle.constant.hash import HASH_ALGORITHMS
import fnmatch
import re

class Text(str):
    """
    A subclass of Python's built-in str, enriched with utility methods
    such as digest generation, wildcard matching, and export support.
    
    """

    def __new__(cls, content: str = ""):
        return super(Text, cls).__new__(cls, content)

    def __init__(self, content: str = ""):
        # no need to set self.content explicitly; str content is the instance itself
        pass

    # --- Lazy Properties ---
    
    @property
    def dict(self) -> Dict[str, str]:
        if not str(self):
            return {}
        else:
            return {"content": str(self)}

    @property
    def upper(self) -> str:
        return str(self).upper()
    
    @property
    def lower(self) -> str:
        return str(self).lower()
    
    @property
    def snake(self) -> str:
        return str(self.to_snake())
    
    @property
    def camel(self) -> str:
        return str(self.to_camel())

    def __repr__(self) -> str:
        preview = str(self)
        if len(preview) > 10:
            preview = f"{preview[:10]}..."
        return f"{self.__class__.__name__}(content={preview})"

    # --- Operations ---
    def __len__(self) -> int:
        return len(str(self))
    
    def __eq__(self, other: Union[str, "Text"]) -> bool:
        if isinstance(other, str):
            return str(self) == other
        elif isinstance(other, Text):
            return super(Text, self).__eq__(other)
        return False
    
    def __ne__(self, other: Union[str, "Text"]) -> bool:
        if isinstance(other, str):
            return str(self) != other
        elif isinstance(other, Text):
            return super(Text, self).__ne__(other)
        return True
    
    def __lt__(self, other: Union[str, "Text"]) -> bool:
        if isinstance(other, str):
            return str(self) < other
        elif isinstance(other, Text):
            return super(Text, self).__lt__(other)
        return False
    
    def __le__(self, other: Union[str, "Text"]) -> bool:
        if isinstance(other, str):
            return str(self) <= other
        elif isinstance(other, Text):
            return super(Text, self).__le__(other)
        return False
    
    def __gt__(self, other: Union[str, "Text"]) -> bool:
        if isinstance(other, str):
            return str(self) > other
        elif isinstance(other, Text):
            return super(Text, self).__gt__(other)
        return False
    
    def __ge__(self, other: Union[str, "Text"]) -> bool:
        if isinstance(other, str):
            return str(self) >= other
        elif isinstance(other, Text):
            return super(Text, self).__ge__(other)
        return False
    
    def __contains__(self, item: Union[str, "Text"]) -> bool:
        if isinstance(item, str):
            return str(item) in str(self)
        elif isinstance(item, Text):
            return super(Text, self).__contains__(item)
        return False
    
    def __add__(self, other: Union[str, "Text"]) -> str:
        if isinstance(other, str):
            return str(self) + other
        elif isinstance(other, Text):
            return super(Text, self).__add__(other)
        return str(self) + str(other)
    
    def __radd__(self, other: Union[str, "Text"]) -> str:
        if isinstance(other, str):
            return other + str(self)
        elif isinstance(other, Text):
            return super(Text, self).__radd__(other)
        return str(other) + str(self)
    
    def __mul__(self, other: int) -> str:
        if isinstance(other, int):
            return str(self) * other
        return str(self) * int(other)
    
    def __rmul__(self, other: int) -> str:
        if isinstance(other, int):
            return str(self) * other
        return str(self) * int(other)
    
    # --- Methods ---

    def as_digest(self, algorithm: str = "sha256") -> "Text":
        """
        Hashes the content using the specified algorithm.
        Available algorithms defined in HASH_ALGORITHMS.
        
        """
        hash_function = HASH_ALGORITHMS[algorithm]
        hash_function.update(self.encode())
        return Text(hash_function.hexdigest())

    def wildcard_match(self, pattern: str) -> bool:
        return fnmatch.fnmatch(str(self), pattern)

    def to_snake(self) -> "Text":
        """
        Converts the string to snake_case.
        
        """
        s = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', str(self))
        s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s)
        return Text(s.lower())

    def to_camel(self) -> "Text":
        """
        Converts the string to camelCase.
        
        """
        parts = str(self).split('_')
        return Text(parts[0] + ''.join(word.capitalize() for word in parts[1:]))

    def export(self) -> Dict[str, Union[str]]:
        return {
            key: value for key, value in self.dict.items()
            if value not in (None, set())
        }