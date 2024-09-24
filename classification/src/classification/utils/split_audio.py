import random
import sys
from pathlib import Path
from typing import Optional

import click
from pydub import AudioSegment
from tqdm import trange

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
    default=10,
    show_default=True,
    type=click.IntRange(min=1),
    help="In how many pieces to split the audio.",
)
@click.option(
    "-d",
    "--duration",
    default=SOUND_DURATION,
    show_default=True,
    type=click.FloatRange(min=0.0, min_open=True),
    help="How long (in seconds) each pieces should be.",
)
@click.option(
    "-s",
    "--seed",
    default=None,
    type=click.IntRange(min=0),
    help="Random seed to use.",
)
@click.option(
    "-z",
    "--zero-padding",
    metavar="WIDTH",
    default=None,
    type=click.IntRange(min=0),
    help="Fill each number with leading zeros until it reaches the given width. "
    "If not specified, computes from `--num-pieces`",
)
@click.option(
    "--directory",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("."),
    show_default=True,
    help="Output directory for generated audio files.",
)
@click.option(
    "-p",
    "--prefix",
    type=str,
    default=None,
    help="Filename prefix for generated audio files. "
    "If not specified, uses SOURCE's filename.",
)
@common.click.verbosity
def main(
    source: Path,
    num_pieces: int,
    duration: float,
    seed: Optional[int],
    zero_padding: Optional[int],
    directory: Path,
    prefix: Optional[str],
) -> None:
    """
    Split SOURCE audio file (.wav) into many pieces of fixed duration.

    The audio is split randomly, and pieces may overlap as they are all
    independently generated.
    """
    width = zero_padding or len(str(num_pieces - 1))

    random.seed(seed)

    logger.info("Reading source audio file...")

    audio = AudioSegment.from_wav(source)

    duration_millis = int(1000 * duration)

    frac = len(audio) / duration_millis

    directory.mkdir(parents=True, exist_ok=True)

    fname = prefix or source.stem

    if frac < 1:
        logger.error(
            "The provided audio file has duration of "
            f"{len(audio) / 1000.0:.0f}s, "
            f"which is shorter than required duration of {duration:.0f}s."
        )
        sys.exit(1)
    else:
        logger.info(
            "The ratio of source duration / required duraction per piece is "
            f"{frac:.2}"
        )

    max_start = len(audio) - duration_millis

    for i in trange(
        num_pieces, desc="Splitting audio files into random pieces...", leave=False
    ):
        start = random.randint(0, max_start)

        piece = audio[start : start + duration_millis]

        piece.export(directory / f"{fname}_{i:0{width}d}.wav", format="wav")
