from abc import ABC, abstractmethod


class BasePath(ABC):
    def __init__(self, raw: str):
        self.raw = raw

    def __str__(self) -> str:
        return self.raw

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(raw={self.raw})"

    @abstractmethod
    def is_absolute(self) -> bool: ...

    @abstractmethod
    def is_remote(self) -> bool: ...

    @abstractmethod
    def to_uri(self) -> str: ...

    def export(self) -> dict:
        return {
            "raw": self.raw,
        }
