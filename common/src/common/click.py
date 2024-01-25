"""
Common wrapper for click applications.
"""
from typing import Any, Callable

import click

from .defaults import MELVEC_LENGTH, N_MELVECS
from .logging import logger

F = Callable[..., Any]
Wrapper = Callable[[F], F]

melvec_length = click.option(
    "-l",
    "--melvec-length",
    default=MELVEC_LENGTH,
    envvar="MELVEC_LENGTH",
    type=click.IntRange(min=0),
    show_default=True,
    show_envvar=True,
    help="Length of one Mel vector.",
)

n_melvecs = click.option(
    "-n",
    "--n-melvecs",
    default=N_MELVECS,
    envvar="N_MELVECS",
    type=click.IntRange(min=0),
    show_default=True,
    show_envvar=True,
    help="Number of Mel vectors per packet.",
)


def verbosity(function: F) -> F:
    """Wrap a function to add verbosity option."""

    def callback(ctx: click.Context, param: click.Parameter, value: str) -> None:
        if not value or ctx.resilient_parsing:
            return

        logger.setLevel(value)

    wrapper: Wrapper = click.option(
        "-v",
        "--verbosity",
        type=click.Choice(
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            case_sensitive=False,
        ),
        help="Verbosity of CLI output.",
        default=None,
        expose_value=False,
        envvar="LELEC210X_VERBOSITY",
        show_envvar=True,
        callback=callback,
    )

    return wrapper(function)
