from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from base import FormatterBase

class MarkdownFormatter(FormatterBase):
    """
    Renders structured class info into a Markdown document using Jinja2 template.
    """

    def __init__(self, template_path: Path):
        super().__init__(template_path)
        self.env = Environment(
            loader=FileSystemLoader(template_path.parent),
            #autoescape=select_autoescape(["html", "xml", "md", "jinja"]),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.template = self.env.get_template(template_path.name)

    def render(self, data: Any) -> str:
        return self.template.render(data)