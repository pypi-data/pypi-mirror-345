from pathlib import Path
import ast
from typing import Any, Dict, List, Optional

with open(
    "/Users/xingxing/Desktop/my-project/x17/pangu/particle/datestamp/date.py", 
    "r", 
    encoding="utf-8",
) as file:
    tree = ast.parse(file.read())
    
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        
        print(f"node.name: {node.name}")
        print(f"node.bases: {[ast.dump(base) for base in node.bases]}")
        print(f"node.docstring: {ast.get_docstring(node)}")
        
        for item in node.body:
            
            if isinstance(item, ast.FunctionDef):
                print(f"  Method: {item.name}")
                print(f"  Args: {[arg.arg for arg in item.args.args]}")
                print(f" Returns: {item.returns}")
                print(f"  Docstring: {ast.get_docstring(item, clean=True)}")
                print(f"  Annotations: {item.returns}")
                
        #     elif isinstance(item, ast.Assign):
        #         for target in item.targets:
        #             if isinstance(target, ast.Name):
        #                 print(f"  Attribute: {target.id}")
        #                 print(f"  - Value: {ast.dump(item.value)}")
        #     else:
        #         print(f"  Other: {ast.dump(item)}")