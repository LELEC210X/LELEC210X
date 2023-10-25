"""
Scripts for extracting code fragment from a node id.

This is taken from https://github.com/jeertmans/pyextract,
with minimal amount of code kept.

This is used to include code fragments in LaTeX, that need
to be re-generated each time.

Usage:
    python extract_code.py "file.py::path:to:function"
"""
import ast
import sys
import textwrap
from pathlib import Path

if __name__ == "__main__":
    node_id = sys.argv[1]

    try:
        path_str, parts_str = node_id.split("::", maxsplit=1)
        path = Path(path_str)
        parts = parts_str.split("::")
    except ValueError:
        path = Path(node_id)
        parts = []

    code = path.read_text()

    if parts:
        tree = ast.parse(code)
        
        for part in parts:
            try:
                tree = next(node for node in tree.body if getattr(node, "name", None) == part)
            except StopIteration as e:
                raise ValueError(f"Could not find {part} in {node_id}") from e

        code = ast.get_source_segment(code, tree, padded=True)

    print(textwrap.dedent(code), end="")
