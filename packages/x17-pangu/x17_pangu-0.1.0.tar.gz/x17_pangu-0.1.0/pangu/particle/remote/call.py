import urllib.request
import urllib.parse
import urllib.error
import json
import time
from typing import Optional, Dict, Any, Union
from pangu.particle.remote.url import Url
from pangu.particle.remote.response import Response
from pangu.particle.log.log_event import LogEvent
from pangu.particle.duration import Duration
from pangu.particle.datestamp.datestamp import Datestamp


class Call:
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Call":
        return cls(
            method=data.get("method", "GET"),
            url=data.get("url", ""),
            headers=data.get("headers", {}),
            query=data.get("query", {}),
            body=data.get("body", None),
            timeout=data.get("timeout", 10),
            retry=data.get("retry", 1),
            interval=data.get("interval", Duration(second=1))
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Call":
        return cls.from_dict(json.loads(json_str))

    def __init__(
        self,
        method: str,
        url: Union[str, Url],
        headers: Optional[Dict[str, str]] = None,
        query: Optional[Dict[str, Any]] = None,
        body: Optional[Union[str, bytes, dict]] = None,
        timeout: int = 10,
        retry: int = 1,
        interval: Duration = Duration(second=1),
    ):
        self.method = method.upper()
        self.url = Url(url=url) if isinstance(url, str) else url
        self.query = query or {}
        self.url = self.url.join_querys(self.query)

        self.headers = headers or {}
        self.headers.setdefault("Accept", "*/*")
        self.headers.setdefault("User-Agent", "Call/1.0")

        self.body = body
        self.timeout = timeout
        self.retry = retry
        self.interval = interval
        self.index = 0
        self.log: list[LogEvent] = []

    @property
    def attr(self) -> list:
        return ["method", "url", "headers", "query", "body", "timeout", "retry", "interval"]

    @property
    def dict(self) -> Dict[str, Any]:
        return {
            "method": self.method,
            "url": str(self.url),
            "headers": self.headers,
            "query": self.query,
            "body": self.body,
            "timeout": self.timeout,
            "retry": self.retry,
            "interval": self.interval,
        }

    def __repr__(self):
        attr_parts = [f"{key}={repr(getattr(self, key))}" for key in self.attr if getattr(self, key, None)]
        return f"{self.__class__.__name__}({', '.join(attr_parts)})"

    def __str__(self):
        return self.__repr__()

    @property
    def data(self) -> bytes:
        """
        Encode request body if present.
        """
        if isinstance(self.body, dict):
            self.headers.setdefault("Content-Type", "application/json")
            return json.dumps(self.body).encode("utf-8")
        elif isinstance(self.body, str):
            return self.body.encode("utf-8")
        elif isinstance(self.body, bytes):
            return self.body
        elif self.body is None:
            return None
        else:
            raise ValueError("Unsupported data type for request body.")

    @property
    def request(self) -> urllib.request.Request:
        return urllib.request.Request(
            url=self.url.link,
            data=self.data,
            headers=self.headers,
            method=self.method,
        )

    def send(self) -> "Response":
        for index in range(self.retry):
            self.index += 1
            status, headers, body, error = 0, {}, b"", ""
            try:
                with urllib.request.urlopen(self.request, timeout=self.timeout) as res:
                    status = res.status
                    headers = dict(res.getheaders())
                    body = res.read()
            except urllib.error.HTTPError as e:
                status = e.code
                headers = dict(e.headers)
                body = e.read()
                error = str(e)
            except Exception as e:
                error = str(e)

            self.log.append(
                LogEvent(
                    message=error or "Request succeeded",
                    name=self.__class__.__name__,
                    level="INFO" if 200 <= status < 300 else "ERROR",
                    datestamp=Datestamp.now().datestamp_str,
                    status=status,
                    body=body,
                    url=self.url,
                    error=error,
                    retry=index + 1,
                    interval=self.interval.second,
                )
            )

            if 200 <= status < 300 or index >= self.retry - 1:
                break
            self.interval.wait()

        return Response(
            status=status,
            headers=headers,
            body=body,
            url=self.url,
            error=error,
        )