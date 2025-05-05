from pathlib import Path
import ast
from typing import Any, Dict, List, Optional
from base import ParserBase

class ClassParser(ParserBase):
    """
    Parses a Python file to extract class-level metadata and structure.
    
    """

    def parse(self) -> List[Dict[str, Any]]:
        with open(self.filepath, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read())

        classes: List[Dict[str, Any]] = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_info: Dict[str, Any] = {
                    "name": node.name,
                    "parents": [self._get_name(base) for base in node.bases],
                    "desc": ast.get_docstring(node),
                    "class_params": [],
                    "attributes": [],
                    "instance_methods": [],
                    "static_methods": [],
                    "class_methods": [],
                }
                
                method_names = {m["name"] for m in class_info["instance_methods"]}
                for m in class_info["instance_methods"]:
                    related = []
                    for other in method_names:
                        if other != m["name"] and (
                            other.startswith(m["name"][:3]) or m["name"][:3] in other
                        ):
                            related.append(other)
                    m["related"] = related
                    
                
                class_info["refs"] = self._extract_imports(tree)

                for body_item in node.body:
                    if isinstance(body_item, ast.FunctionDef) and body_item.name == "__init__":
                        for arg in body_item.args.args[1:]:  # skip self
                            class_info["class_params"].append({
                                "name": arg.arg,
                                "type": self._get_annotation(arg.annotation),
                                "desc": "",
                                "optional": False,
                                "default": None,
                            })

                    # attribute assignment
                    if isinstance(body_item, ast.Assign):
                        for target in body_item.targets:
                            if isinstance(target, ast.Name):
                                class_info["attributes"].append({
                                    "name": target.id,
                                    "type": "Any",
                                    "desc": "",
                                })

                    # methods
                    if isinstance(body_item, ast.FunctionDef):
                        method = {
                            "name": body_item.name,
                            "params": [
                                {
                                    "name": arg.arg,
                                    "type": self._get_annotation(arg.annotation),
                                    "desc": ""
                                } for arg in body_item.args.args[1:]
                            ],
                            "returns": [{
                                "type": self._get_annotation(body_item.returns),
                                "desc": self._get_docstring(body_item.returns),
                            }] if body_item.returns else [],
                            "desc": ast.get_docstring(body_item),
                        }

                        decorators = [self._get_name(d) for d in body_item.decorator_list]
                        if "staticmethod" in decorators:
                            class_info["static_methods"].append(method)
                        elif "classmethod" in decorators:
                            class_info["class_methods"].append(method)
                        else:
                            class_info["instance_methods"].append(method)

                classes.append(class_info)

        return classes

    def _get_annotation(self, node: Optional[ast.AST]) -> str:
        if node is None:
            return "Any"
        try:
            return ast.unparse(node)
        except Exception:
            return "Any"

    def _get_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        try:
            return ast.unparse(node)
        except Exception:
            return "Unknown"
        
    def _extract_imports(self, tree: ast.Module) -> List[str]:
        imports = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module:
                    imports.append(module)
        return sorted(set(imports))
    
    def _get_docstring(self, node: Optional[ast.AST]) -> str:
        if node is None:
            return ""
        if isinstance(node, ast.Constant):
            return node.value
        return ""