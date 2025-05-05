from typing import List, Optional, Dict, Any, Union
from pangu.particle.remote.call import Call
from pangu.particle.remote.response import Response
from pangu.particle.log.log_event import LogEvent

class CallSet:
    def __init__(self, calls: Optional[List[Call]] = None):
        self.calls: List[Call] = calls or []
        self.results: List[Response] = []
        self.logs: List[LogEvent] = []

    def add(self, call: Call):
        self.calls.append(call)

    def batch(self, call_data: List[Dict[str, Any]]):
        for data in call_data:
            self.calls.append(Call.from_dict(data))

    def run(self) -> List[Response]:
        self.results.clear()
        self.logs.clear()

        for call in self.calls:
            response = call.send()
            self.results.append(response)
            self.logs.extend(call.log)

        return self.results

    @property
    def attr(self) -> List[str]:
        return ["calls", "results", "logs"]

    @property
    def dict(self) -> Dict[str, Any]:
        return {
            "calls": [c.dict for c in self.calls],
            "results": [r.dict for r in self.results],
            "logs": [l.dict for l in self.logs],
        }

    def __repr__(self):
        return f"CallSet(calls={len(self.calls)}, results={len(self.results)})"

    def __str__(self):
        return self.__repr__()