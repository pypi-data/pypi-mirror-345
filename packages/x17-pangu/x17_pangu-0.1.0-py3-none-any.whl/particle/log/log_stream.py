from __future__ import annotations
import logging
from typing import Optional
from typing import TYPE_CHECKING

from pangu.particle.text.id import Id
from pangu.particle.log.log_event import LogEvent
if TYPE_CHECKING:
    from pangu.particle.log.log_group import LogGroup


class LogStream:
    def __init__(
        self,
        name: Optional[str] = "",
        group: Optional[LogGroup] = None,
        format: Optional[str] = None,
        verbose: Optional[bool] = False,
        **kwargs,
    ):
        self.id = Id.uuid(8)
        self.base_name = name
        self.name = name or f"{self.__class__.__name__}:{self.id}"
        self.group = group or None
        self.log_format = format or "[%(asctime)s][%(levelname)s][%(name)s] %(message)s"
        self.log_node = self._setup_node()
        self.verbose = verbose

    @property
    def attr(self) -> list[str]:
        return [
            "id",
            "name",
            "group",
            "log_format",
        ]

    @property
    def dict(self) -> dict[str, str]:
        return {key: getattr(self, key) for key in self.attr}

    def __repr__(self):
        attr_parts = []
        for key in self.attr:
            value = getattr(self, key, None)
            attr_parts.append(f"{key}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attr_parts)})"

    def __str__(self):
        return self.__repr__()

    def _setup_node(self):
        log_node = logging.getLogger(f"LogStream:{self.name}")
        if not log_node.handlers:
            log_node.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(self.log_format)
            handler.setFormatter(formatter)
            log_node.addHandler(handler)
        return log_node

    def log(self, message: str, level: str = "INFO"):
        event = LogEvent(level=level, message=message)
        if self.group:
            self.group.receive(self.name, event)
        
        if self.verbose:
            self.log_node.log(
                getattr(logging, level.upper(), logging.INFO),
                message,
            )

    def info(self, message: str):
        self.log(message, "INFO")

    def warn(self, message: str):
        self.log(message, "WARNING")

    def error(self, message: str):
        self.log(message, "ERROR")

    def debug(self, message: str):
        self.log(message, "DEBUG")
