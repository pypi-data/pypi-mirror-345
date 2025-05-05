import argparse
from pathlib import Path
from generator import DocGenerator
import os

def collect_py_files(source_path: Path) -> list[Path]:
    if source_path.is_file():
        return [source_path]
    return list(source_path.rglob("*.py"))

def main(source: str = None, template: str = None, output: str = None):
    if (not source or not template or not output):
        source_path = Path("./")
        template_path = Path("./doc/template/class_doc_template.md.jinja")
        output_dir = Path("./doc/output/")
    else:
        parser = argparse.ArgumentParser(description="Generate class documentation from Python files.")
        parser.add_argument("--source", type=str, required=True, help="Path to a .py file or a directory.")
        parser.add_argument("--template", type=str, required=True, help="Path to Jinja markdown template.")
        parser.add_argument("--output", type=str, required=True, help="Directory to output Markdown files.")

        args = parser.parse_args()
        source_path = Path(args.source)
        template_path = Path(args.template)
        output_dir = Path(args.output)

    all_files = collect_py_files(source_path)
    print(f"[docgen] Found {len(all_files)} Python files to process.")
    if not all_files:
        print("[docgen] No Python files found.")
        return
    
    if not template_path.exists():
        os.makedirs(template_path.parent, exist_ok=True)

    for py_file in all_files:
        generator = DocGenerator(
            source=py_file,
            template=template_path,
            output_dir=output_dir,
        )
        generator.generate()

if __name__ == "__main__":
    main()
    



# python ./doc/gen/run.py \
#   --source ./particle \
#   --template ./doc/template/class_doc_template.md.jinja \
#   --output ./doc/output/