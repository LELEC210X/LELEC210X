import random
import time
from pathlib import Path
from threading import Thread
from typing import Optional

import click
import requests
from pydub import AudioSegment
from pydub.utils import register_pydub_effect

from classification.datasets import Dataset
from common.click import verbosity
from common.logging import logger

from .utils import get_url

session = requests.Session()


@register_pydub_effect
def normalize_dBFS(  # noqa: N802
    seg: AudioSegment,
    target_dBFS: float = -20,  # noqa: N803
) -> AudioSegment:
    """
    Normalize an audio segment to a given loudness (dBFS).

    The loudness of the audio segment is determined by the
    average energy of each audio sample.
    """
    gain = target_dBFS - seg.dBFS

    return seg.apply_gain(gain)


@click.command()
@click.option(
    "-u",
    "--url",
    default=None,
    envvar="LEADERBOARD_URL",
    show_default=True,
    show_envvar=True,
    help="Base API url. If not specified, will use FLASK_RUN_HOST and FLASK_RUN_PORT.",
)
@click.option(
    "-k",
    "--key",
    required=True,
    envvar="LEADERBOARD_ADMIN_KEY",
    show_envvar=True,
    help="Key granting admin rights.",
)
@click.option(
    "-r",
    "--random-key",
    default=None,
    envvar="LEADERBOARD_RANDOM_KEY",
    show_envvar=True,
    help="Key for a group that will always guess randomly. "
    "This is useful to compare your performances to a random classifier.",
)
@click.option(
    "--soundfiles",
    default=None,
    envvar="LEADERBOARD_SOUNDFILES",
    show_envvar=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="An optional path to a directory that contains soundfiles. "
    "This may be used during the contest to use different soundfiles.",
)
@click.option(
    "--format",
    "_format",
    default="wav",
    envvar="LEADERBOARD_SOUNDFILES_FORMAT",
    show_envvar=True,
    help="The sound files format to include, use '*' to include all formats.",
)
@verbosity
def play_sound(
    url: Optional[str],
    key: str,
    random_key: Optional[str],
    soundfiles: Optional[Path],
    _format=Optional[str],
):
    """
    Play "correct" sound according to the leaderboard status.

    Admin group will always guess to correct class.

    If specified, random group will guess classes randomly.

    Both groups always submit guesses during the valid timing window,
    so they never have any penalty on that regard.
    """
    from pydub import AudioSegment
    from pydub.generators import WhiteNoise
    from pydub.playback import play

    url = url or get_url()

    dataset_kwargs = {}

    if soundfiles:
        dataset_kwargs["soundfiles"] = soundfiles

    if soundfiles:
        dataset_kwargs["format"] = _format

    dataset = Dataset(**dataset_kwargs)

    # Wait for server to be up
    # and checks if admin rights
    while True:
        logger.debug("Checking if the server is up and the admin key is valid.")
        # Timeout issue?
        # https://stackoverflow.com/questions/70917108/python-requests-get-only-responds-if-adding-a-time-out
        response = session.get(f"{url}/lelec210x/leaderboard/check/{key}", timeout=1)

        code = response.status_code

        if code == 200:
            assert response.json()["admin"], "key must belong to an admin!"

            if random_key:
                logger.debug("Checking if the server is up and the 'random' is valid.")
                response = session.get(
                    f"{url}/lelec210x/leaderboard/check/{random_key}",
                    timeout=1,
                )

                if response.status_code != 200:
                    raise ValueError(response.json())

            break
        elif code == 401:
            raise ValueError(response.json())
        else:
            logger.info("Waiting server to be ready...")
            time.sleep(0.2)

    played_sounds = set()

    while True:
        start = time.time()
        json = session.get(
            f"{url}/lelec210x/leaderboard/status/{key}", timeout=1
        ).json()
        delay = time.time() - start
        logger.info(f"Took {delay:.4f}s for the status request.")

        if json["paused"]:
            logger.info("Leaderboard is paused...")
            time.sleep(0.2)
            continue

        logger.info(str(json))

        current_round = json["current_round"]
        current_lap = json["current_lap"]
        time_before_next_lap = json["time_before_next_lap"]
        time_before_playing = json["time_before_playing"]
        category = json["current_correct_guess"]
        with_noise = json["current_with_noise"]

        sound_key = (current_round + 1, current_lap + 1)

        if sound_key in played_sounds:
            logger.info(f"A song has already been played for round, lap: {sound_key}.")
            time.sleep(time_before_next_lap)
            continue

        played_sounds.add(sound_key)

        sound_file = random.choice(dataset.get_class_files(category))

        if time_before_playing < 0:
            logger.info(f"Too late for playing: {category}.")
            time.sleep(time_before_next_lap)
            continue

        logger.info(f"Playing sound in {time_before_playing}.")

        start = time.time()
        sound = (
            AudioSegment.from_file(sound_file, format=_format)
            .set_channels(1)
            .normalize_dBFS()
            .fade_in(250)
            .fade_out(250)
        )

        if with_noise and current_lap >= 8:
            relative_gain = -16 + 4 * (current_lap - 8)
            logger.info(
                "Adding random noise on top of audio segment "
                f"with a relative volume gain of {relative_gain} dB."
            )
            sound = sound.overlay(
                WhiteNoise().to_audio_segment(
                    duration=len(sound), volume=sound.dBFS + relative_gain
                )
            )

        time.sleep(time_before_playing - max(0, time.time() - start))

        thread = Thread(target=play, args=(sound,))
        thread.start()
        logger.info(f"Playing sound now: {sound_file}.")

        # Admins are always correct :-)
        session.post(f"{url}/lelec210x/leaderboard/submit/{key}/{category}", timeout=1)

        if random_key:  # Random player
            guess = random.choice(dataset.list_classes())
            session.post(
                f"{url}/lelec210x/leaderboard/submit/{random_key}/{guess}", timeout=1
            )

        thread.join()
