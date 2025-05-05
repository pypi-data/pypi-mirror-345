from urllib.parse import urlparse, urlunparse, urlencode, parse_qs
from typing import Optional, Dict, Any, List, Union


class Url:
    """
    RemoteURL 是用于远程访问资源的统一地址抽象，支持：
    - 从字符串解析 URL
    - 拼接 path、添加 query 参数
    - 导出为标准 URL 字符串或结构化字典

    """

    @classmethod
    def from_str(cls, url_str: str) -> "Url":
        parsed = urlparse(url_str)
        return cls(
            scheme=parsed.scheme,
            host=parsed.hostname or "",
            port=parsed.port,
            path=parsed.path,
            query=parse_qs(parsed.query),
            user=parsed.username,
            password=parsed.password,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Url":
        return cls(
            scheme=data.get("scheme", "https"),
            host=data.get("host", ""),
            port=data.get("port"),
            path=data.get("path", ""),
            query=data.get("query", {}),
            user=data.get("user"),
            password=data.get("password"),
        )

    def __init__(
        self,
        url=None,
        scheme: str = "https",
        host: str = "",
        port: Optional[int] = None,
        path: str = "",
        query: Optional[Dict[str, Any]] = {},
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):

        if url:
            result = urlparse(url)
            self.scheme = result.scheme or scheme
            self.host = result.hostname or host
            self.port = result.port or port
            self.path = result.path or path
            
            parsed_query = parse_qs(result.query or "")
            self.query = parsed_query.copy()
            if query:
                self.query.update(query)

            self.user = result.username or user
            self.password = result.password or password
        else:
            self.scheme = scheme
            self.host = host
            self.port = port
            self.path = path or ""
            self.query = query.copy() if query else {}
            self.user = user
            self.password = password

    @property
    def link(self) -> str:
        endpoint = self.host
        if self.port:
            endpoint += f":{self.port}"
        if self.user:
            auth = f"{self.user}:{self.password}@" if self.password else f"{self.user}@"
            endpoint = auth + endpoint
        query_str = urlencode(self.query, doseq=True)
        return urlunparse((self.scheme, endpoint, self.path, "", query_str, ""))

    @property
    def attr(self) -> list[str]:
        return [
            "link",
            "scheme",
            "host",
            "port",
            "path",
            "query",
            "user",
            "password",
        ]

    @property
    def dict(self) -> dict:
        return {key: getattr(self, key) for key in self.attr}

    def __repr__(self):
        attr_parts = []
        for key in self.attr:
            value = getattr(self, key, None)
            if value:
                attr_parts.append(f"{key}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attr_parts)})"

    def __str__(self):
        return self.link

    def __truediv__(self, segment: str) -> "Url":
        return self.join_path(segment)

    def __add__(self, other: str) -> "Url":
        return self.join_path(other)

    def __radd__(self, other: str) -> "Url":
        return self.join_path(other)

    def join_path(self, *segments: Union[str, List[str]]) -> "Url":
        joined_path = (
            self.path.rstrip("/") + "/" + "/".join(s.strip("/") for s in segments)
        )
        return Url(
            scheme=self.scheme,
            host=self.host,
            port=self.port,
            path=joined_path,
            query=self.query.copy(),
            user=self.user,
            password=self.password,
        )
        
    def join_querys(self, query: Dict[str, Any]) -> "Url":
        for key, value in query.items():
            self.join_query(key, value)
        return self

    def join_query(self, key: str, value: Any) -> "Url":
        if key in self.query:
            existing = self.query[key]
            if isinstance(existing, list):
                existing.append(value)
            else:
                self.query[key] = [existing, value]
        else:
            self.query[key] = value
        return self

    def remove_query(self, key: str) -> "Url":
        if key in self.query:
            del self.query[key]
        return self

    def parent(self) -> "Url":
        parts = self.path.rstrip("/").split("/")
        if len(parts) > 1:
            parent_path = "/".join(parts[:-1])
        else:
            parent_path = "/"
        return Url(
            scheme=self.scheme,
            host=self.host,
            port=self.port,
            path=parent_path,
            query=self.query.copy(),
            user=self.user,
            password=self.password,
        )

    def redact(self) -> "Url":
        return Url(
            scheme=self.scheme,
            host=self.host,
            port=self.port,
            path=self.path,
            query=self.query.copy(),
            user=self.user,
            password="****" if self.password else None,
        )

    def export(self) -> Dict[str, Any]:
        return {
            "url": self.link,
            "scheme": self.scheme,
            "host": self.host,
            "port": self.port,
            "path": self.path,
            "query": self.query,
            "user": self.user,
            "password": self.password,
        }
