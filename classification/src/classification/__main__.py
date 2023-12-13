import pickle
from pathlib import Path
from typing import Optional

import click

from auth import PRINT_PREFIX

from .utils import payload_to_melvecs


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
@click.option(
    "-l",
    "--melvec-len",
    default=20,
    envvar="MELVEC_LEN",
    type=click.IntRange(min=0),
    show_default=True,
    show_envvar=True,
    help="Length of one Mel vector.",
)
@click.option(
    "-n",
    "--num-melvecs",
    default=10,
    envvar="NUM_MELVECS",
    type=click.IntRange(min=0),
    show_default=True,
    show_envvar=True,
    help="Number of Mel vectors per packet.",
)
def main(
    _input: Optional[click.File],
    model: Optional[Path],
    melvec_len: int,
    num_melvecs: int,
) -> None:
    """
    Extract Mel vectors from payloads and perform classification on them.
    Classify MELVECs contained in payloads (from packets).
    """
    if model:
        with open(model, "rb") as file:
            m = pickle.load(file)
    else:
        m = None

    for payload in _input:
        if PRINT_PREFIX in payload:
            payload = payload[len(PRINT_PREFIX) :]

            melvecs = payload_to_melvecs(payload)

            if m:
                # TODO: perform classification
                pass
