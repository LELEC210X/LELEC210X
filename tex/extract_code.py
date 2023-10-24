"""
Scripts for extracting code fragment from a node id.

This is taken from https://github.com/jeertmans/pyextract,
with minimal amount of code kept.

This is used to include code fragments in LaTeX, that need
to be re-generated each time.

Usage:
    python extract_code.py "file.py::path:to:function"
"""
import importlib.util
import inspect
import random
import string
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

    name = basename = path.resolve(strict=True).stem

    while name in sys.modules:  # To avoid name clash with already imported modules
        name = (
            basename
            + "_"
            + "".join(random.choice(string.ascii_letters) for i in range(8))
        )

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    obj = module

    for part in parts:
        obj = getattr(obj, part)

    lines, _ = inspect.getsourcelines(obj)

    print(textwrap.dedent("".join(lines)), end="")
