from __future__ import annotations
from typing import Optional, List, Dict, Any

from pangu.particle.datestamp import Datestamp
from pangu.particle.text.id import Id


class LogEvent:

    def from_dict(self, data: Dict[str, Any]) -> LogEvent:
        """
        Create a LogEvent instance from a dictionary.

        """
        return LogEvent(
            message=data.get("message", ""),
            level=data.get("level", "INFO"),
            datestamp=data.get("datestamp", None),
        )

    def __init__(
        self,
        message: str,
        name: Optional[str] = "",
        level: str = "INFO",
        datestamp: Optional[str] = None,
        **kwargs: Any,
    ):
        self.id = Id.uuid(5)
        self.base_name = name
        self.name = f"{name}:{self.id}" or f"{self.__class__.__name__}:{self.id}"
        self.datestamp = datestamp or Datestamp.now().datestamp_str
        self.level = level.upper()
        self.message = message
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        attr_parts = []
        for key in self.attr:
            value = getattr(self, key, None)
            attr_parts.append(f"{key}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attr_parts)})"

    def __str__(self):
        return self.__repr__()

    @property
    def attr(self) -> List[str]:
        return [
            key for key in self.__dict__.keys()
            if not key.startswith("_")
        ]

    @property
    def dict(self) -> Dict[str, Any]:
        return {key: getattr(self, key) for key in self.attr}

    def export(self) -> Dict[str, str]:
        return self.dict
