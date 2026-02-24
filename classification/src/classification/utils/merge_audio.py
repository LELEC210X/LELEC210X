import random
import sys
from pathlib import Path

import click
import numpy as np
from pydub import AudioSegment
from tqdm import trange

import common
from common.logging import logger

from ..datasets import SOUND_DURATION

def get_shot_offset_ms(audio: AudioSegment) -> float:
    """Return time (ms) of strongest impulse in full clip."""
    samples = np.array(audio.get_array_of_samples())
    peak_index = np.argmax(np.abs(samples))
    return (peak_index / audio.frame_rate) * 1000

def random_time_gen(n, start, end, min_dist):
    """
    Generate n floats in [start, end] with at least min_dist between them.
    """
    total_range = end - start
    required_space = min_dist * (n - 1)

    slack = total_range - required_space

    if slack < 0:
        raise ValueError("Range too small for the given n and min_dist")

    random_gaps = np.random.rand(n + 1)
    scaled_gaps = random_gaps / random_gaps.sum() * slack
    scaled_gaps[1:] += min_dist
    return start + np.cumsum(scaled_gaps)

@click.command()
@click.argument(
    "sources",
    nargs=-1,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "-n",
    "--num_clips",
    default=10,
    show_default=True,
    type=click.IntRange(min=1),
    help="How many audio clips to produce.",
)
@click.option(
    "-d",
    "--duration",
    default=SOUND_DURATION,
    show_default=True,
    type=click.FloatRange(min=0.0, min_open=True),
    help="How long each clip should be. (s)",
)
@click.option(
    "-s",
    "--seed",
    default=None,
    type=click.IntRange(min=0),
    help="Random seed to use.",
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
    default="gunshots",
    help="Filename prefix for generated audio files. "
    "If not specified, uses SOURCE's filename.",
)
@click.option(
    "-o",
    "--occurences",
    default=3,
    show_default=True,
    type=click.IntRange(min=1),
    help="How occurences of the sound to play.",
)
@click.option(
    "-t",
    "--time_delta",
    default=1,
    show_default=True,
    type=click.IntRange(min=0),
    help="Minimal time between sounds. (s)",
)
@click.option(
    "--slack",
    default=500,
    show_default=True,
    type=click.IntRange(min=0),
    help="Slack at the beginning and end of the clip. (ms)",
)
@common.click.verbosity
def main(
    sources: tuple[Path, ...],
    num_clips: int,
    occurences: int,
    duration: float,
    time_delta: float,
    slack: float,
    seed: int | None,
    directory: Path,
    prefix: str | None,
) -> None:

    random.seed(seed)
    directory.mkdir(parents=True, exist_ok=True)

    duration_ms = duration * 1000
    delta_ms = time_delta * 1000

    cache: dict[Path, tuple[AudioSegment, float]] = {}

    for clip_index in trange(num_clips, desc="Generating audio files..."):
        piece = AudioSegment.silent(duration=int(duration_ms))

        max_start = duration_ms - (occurences - 1) * delta_ms
        if max_start < 0:
            raise ValueError("Duration too short for required occurrences and time_delta.")

        shot_times = random_time_gen(occurences,
                                     slack, duration_ms - slack,
                                     delta_ms)

        for shot_time,path in zip(shot_times,random.choices(sources, k = occurences)):
            if path not in cache:
                audio = AudioSegment.from_wav(path)
                audio = audio.apply_gain(-audio.max_dBFS)
                shot_offset = get_shot_offset_ms(audio)
                cache[path] = (audio, shot_offset)

            audio, shot_offset = cache[path]

            overlay_position = shot_time - shot_offset

            piece = piece.overlay(audio, position=int(overlay_position))

        filename = f"{prefix or 'clip'}_{clip_index:02d}.wav"
        piece.export(directory / filename, format="wav")
