from typing import List
from .path import BasePath


class BaseFolder:
    def __init__(self, path: BasePath):
        self.path = path

    def list_files(self) -> List[str]:
        raise NotImplementedError("list_files() must be implemented by subclass")

    def list_folders(self) -> List[str]:
        raise NotImplementedError("list_folders() must be implemented by subclass")

    def mkdir(self, exist_ok=True):
        raise NotImplementedError("mkdir() must be implemented by subclass")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path})"

    def export(self) -> dict:
        return {
            "path": str(self.path),
        }
