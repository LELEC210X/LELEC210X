import pickle
from pathlib import Path
from typing import Optional

import click

import common
from common.logging import logger

from ..datasets import SOUND_DURATION


@click.command()
@click.argument(
    "source",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "-n",
    "--num_pieces",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="In how many pieces to split the audio.",
)
@click.option(
    "-d",
    "--duration",
    default=SOUND_DURATION,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="In how many pieces to split the audio.",
)
@click.option(
    "-s",
    "--seed",
    default=None,
    type=int,
    help="Random seed to use.",
)
@common.click.verbosity
def main(
    source: Path,
    num_pieces: int,
    duration: float,
    seed: Optional[int],
) -> None:
    """
    Split one audio file into many pieces of fixed duration.
    """
    pass
