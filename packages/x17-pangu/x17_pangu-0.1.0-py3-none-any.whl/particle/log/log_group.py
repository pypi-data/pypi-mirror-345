import queue
import threading
from typing import Dict, List, Optional, Any
from pangu.particle.log.log_event import LogEvent
from pangu.particle.log.log_stream import LogStream
from pangu.particle.log.log_core import LogCore

from pangu.particle.text.id import Id
from pangu.particle.datestamp import Datestamp


class LogGroup:
    def __init__(
        self,
        name: Optional[str] = "",
        core: Optional[LogCore] = None,
    ):
        self.id = Id.uuid(8)
        self.base_name = name
        self.name = name or f"{self.__class__.__name__}:{self.id}"
        self.core = core
        if self.core:
            self.core.register_group(self)
        self.streams: Dict[str, List[LogEvent]] = {}
        self.queue: queue.Queue = queue.Queue()
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._consume, daemon=True)
        self._thread.start()

    @property
    def attr(self) -> list[str]:
        return [
            "id",
            "name",
            "core",
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

    def register_stream(self, stream: LogStream):
        stream.group = self
        self.streams[stream.name] = []
        return stream

    def receive(self, stream_name: str, event: LogEvent):
        self.queue.put((stream_name, event))

    def _consume(self):
        while True:
            stream_name, event = self.queue.get()
            with self._lock:
                self.streams.setdefault(stream_name, []).append(event)
            if self.core:
                self.core.push(self.name, stream_name, event)

    def export(self) -> Dict[str, List[Dict[str, Any]]]:
        with self._lock:
            return {
                stream: [e.export() for e in events]
                for stream, events in self.streams.items()
            }
