from pathlib import Path
from typing import Union
from parser import ClassParser
from formatter import MarkdownFormatter


class DocGenerator:
    DEFAULT_CLASS_METADATA = {
        "type": {
            "functionalities": [],
            "structures": [],
            "roles": [],
        },
        "parents": [],
        "refs": [],
        "desc": "",
        "usage": "",
        "thread_safe": False,
        "mutable": False,
        "design_patterns": [],
        "deprecated": False,
        "author": "",
    }
    
    """
    Combines a parser and a formatter to generate documentation.
    """

    def __init__(
        self,
        source: Union[str, Path],
        template: Union[str, Path],
        output_dir: Union[str, Path],
    ):
        self.source = Path(source)
        self.template = Path(template)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.parser = ClassParser(self.source)
        self.formatter = MarkdownFormatter(self.template)

    def generate(self):
        classes = self.parser.parse()

        for class_doc in classes:
            if class_doc["name"].lower().startswith("test"):
                continue
            
            if "tests" in str(self.source):
                continue
            
            class_doc.setdefault("path", str(self.source))
            class_doc.setdefault("module", str(self.source.parent))
            
            for key, default_value in self.DEFAULT_CLASS_METADATA.items():
                class_doc.setdefault(key, default_value)
                
            class_name = class_doc.get("name", "unknown")
            class_module = class_doc.get("module", "module")
            output_file = self.output_dir / f"{class_module}/{class_name}.md"
            rendered = self.formatter.render(class_doc)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(rendered, encoding="utf-8", errors="replace", )
            print(f"[docgen] Generated: {output_file}")