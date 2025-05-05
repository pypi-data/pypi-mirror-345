from typing import Optional, Dict, Any, Union, List
import json

from pangu.particle.datestamp.datestamp import Datestamp
from pangu.particle.log.log_event import LogEvent
from pangu.particle.remote.url import Url

class Response:
    """
    Represents an HTTP response.

    """

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Response":
        return cls(
            status=data.get("status", 0),
            headers=data.get("headers", {}),
            body=data.get("body", b""),
            url=data.get("url", ""),
            error=data.get("error", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Response":
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __init__(
        self,
        status: int = 0,
        headers: dict = {},
        body: bytes = b"",
        url: str = "",
        error: str = "",
    ):
        self.status = status
        self.headers = headers
        self.body = body
        self.url = Url(url) if not isinstance(url, Url) else url
        self.error = error

    @property
    def attr(self) -> List[str]:
        return [
            "status",
            "headers",
            "body",
            "url",
            "error",
        ]

    @property
    def dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "headers": self.headers,
            "body": self.body,
            "url": self.url,
            "error": self.error,
        }

    @property
    def success(self) -> bool:
        return 200 <= self.status < 300

    @property
    def encoding(self) -> str:
        content_type = self.headers.get("Content-Type", "")
        if "charset=" in content_type:
            return content_type.split("charset=")[-1].strip()
        return "utf-8"

    @property
    def text(self) -> str:
        return self.body.decode(self.encoding, errors="replace")

    @property
    def log(self) -> LogEvent:
        return [
            LogEvent(
                message=self.text,
                name=self.__class__.__name__,
                level="INFO" if self.success else "ERROR",
                datestamp=Datestamp.now().datestamp_str,
                status=self.status,
                body=self.body.decode(self.encoding, errors="replace"),
                url=str(self.url),
                error=self.error,
            )
        ]

    def __repr__(self):
        attr_parts = []
        for key in self.attr:
            value = getattr(self, key, None)
            if value:
                attr_parts.append(f"{key}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attr_parts)})"

    def __str__(self):
        return self.__repr__()

    def json(self, check=True) -> Union[Dict[str, Any], Any]:
        try:
            return json.loads(self.text)
        except Exception as e:
            if check:
                raise e
            return {}

    def export(
        self,
    ) -> Dict[str, Any]:
        return self.dict

