from pathlib import Path
from typing import Optional

import click

from auth import PRINT_PREFIX


@click.command()
@click.option(
    "-i",
    "--input",
    "_input",
    default="-",
    type=click.File("r"),
    help="Where to read the input stream. Default to '-', a.k.a. stdin.",
)
@click.option(
    "-m",
    "--model",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to the trained classification model.",
)
def main(
    _input: Optional[click.File],
    model: Optional[Path],
) -> None:
    """
    Extract Mel vectors from payloads and perform classification on them.
    Classify MELVECs contained in payloads (from packets).
    """
    # TODO:
    # m = read_from_file(model)

    for payload in _input:
        if PRINT_PREFIX in payload:
            print("classify", payload)
