from pathlib import Path
from abc import ABC, abstractmethod
from typing import Any


class ParserBase(ABC):
    """
    Abstract base class for all class parsers.
    Implementations should return structured class information.
    
    """
    def __init__(self, filepath: Path):
        self.filepath = filepath

    @abstractmethod
    def parse(self) -> Any:
        pass


class FormatterBase(ABC):
    """
    Abstract base class for all formatters.
    Implementations should render structured class info to a string (e.g., Markdown).
    
    """
    def __init__(self, template_path: Path):
        self.template_path = template_path

    @abstractmethod
    def render(self, data: Any) -> str:
        pass