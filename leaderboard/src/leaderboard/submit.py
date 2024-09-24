import json
from typing import Optional

import click
import requests

from common.logging import logger

from .utils import get_url


@click.command()
@click.argument(
    "guess",
)
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
    envvar="LEADERBOARD_KEY",
    show_envvar=True,
    help="Your private key.",
)
def submit(
    guess: str,
    url: Optional[str],
    key: str,
):
    """
    Submit a guess to the leaderboard.
    """
    url = url or get_url()

    response = requests.post(f"{url}/lelec210x/leaderboard/submit/{key}/{guess}")

    response_as_dict = json.loads(response.text)

    if response.status_code == 200:
        logger.info(response_as_dict)
    else:
        logger.error(response_as_dict)
