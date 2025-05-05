# -*- coding: utf-8 -*-
from typing import Any, Dict, Optional
import warnings


class SemiStruct(dict):
    """
    A structured dictionary-like container that restricts native dict operations
    and encourages use of controlled methods like `.get()`, `.put()`, and `.merge()`.
    
    """
    def __init__(
        self, 
        data: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
    ):
        super().__init__(data or {})
        
        self.initialized = True
        self.name = name
        
    
    def put(self, key: str, value: Any) -> None:
        self[key] = value
        
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return super().get(key, default)
    
    def remove(self, key: str) -> None:
        if key in self:
            del self[key]
            
    def update(self, other: Dict[str, Any]) -> None:
        for k, v in other.items():
            self[k] = v
            
    # --- Forbidded native methods ---

    def warn(
        self,
        message: str,
        category: type = UserWarning,
        stacklevel: int = 2,
    ):
        warnings.warn(message, category=category, stacklevel=stacklevel)

    def __getitem__(self, key):
        self.warn(
            f"[SemiStruct] Direct access `obj[{key!r}]` is disabled. Use `.get({key!r})` instead. This access will be ignored.",
        )
        pass

    def __setitem__(self, key, value):
        self.warn(
            f"[SemiStruct] Direct assignment `obj[{key!r}] = {value!r}` is disabled. Use `.put({key!r}, {value!r})` instead.",
        )
        pass

    def update(self, *args, **kwargs):
        self.warn(
            "[SemiStruct] `update()` is disabled. Use `.merge()` instead.",
        )
        pass

    def pop(self, *args, **kwargs):
        self.warn(
            "[SemiStruct] `pop()` is disabled. Use `.remove()` instead.",
        )
        pass

    
    