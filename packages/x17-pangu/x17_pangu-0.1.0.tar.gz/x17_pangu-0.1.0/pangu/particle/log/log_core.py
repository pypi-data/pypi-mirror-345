import queue
import threading
from typing import Dict, List, Optional, Any
from typing import TYPE_CHECKING

from pangu.particle.text.id import Id
from pangu.particle.log.log_event import LogEvent
if TYPE_CHECKING:
    from pangu.particle.log.log_group import LogGroup


class LogCore:
    def __init__(
        self,
        name: Optional[str] = "",
    ):
        self.id = Id.uuid(8)
        self.base_name = name
        self.name = name or f"{self.__class__.__name__}:{self.id}"
        self.groups: Dict[str, Dict[str, List[LogEvent]]] = {}
        self.queue: queue.Queue = queue.Queue()
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._consume, daemon=True)
        self._thread.start()

    def register_group(self, group: "LogGroup") -> str:
        with self._lock:
            self.groups.setdefault(group.name, {})
        group.core = self
        return group.name

    def push(self, group: str, stream: str, event: LogEvent):
        self.queue.put((group, stream, event))

    def _consume(self):
        while True:
            group, stream, event = self.queue.get()
            with self._lock:
                self.groups.setdefault(group, {}).setdefault(stream, []).append(event)

    def export(self, group: Optional[str] = None, stream: Optional[str] = None) -> Any:
        with self._lock:
            if group is None:
                return {
                    g: {s: [e.export() for e in streams] for s, streams in grp.items()}
                    for g, grp in self.groups.items()
                }
            if stream is None:
                return {
                    s: [e.export() for e in self.groups.get(group, {}).get(s, [])]
                    for s in self.groups.get(group, {})
                }
            return [e.export() for e in self.groups.get(group, {}).get(stream, [])]
