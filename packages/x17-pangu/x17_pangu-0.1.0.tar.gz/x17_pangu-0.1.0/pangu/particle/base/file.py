from typing import Optional
from .path import BasePath


class BaseFile:
    def __init__(self, path: BasePath, content: Optional[str] = None):
        self.path = path
        self.content = content

    def read(self) -> str:
        raise NotImplementedError("read() must be implemented by subclass")

    def write(self, content: str):
        raise NotImplementedError("write() must be implemented by subclass")

    def exists(self) -> bool:
        raise NotImplementedError("exists() must be implemented by subclass")

    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "content": self.content,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path})"

    def export(self) -> dict:
        return {
            "path": str(self.path),
            "content": self.content,
        }
