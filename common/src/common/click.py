"""
Common wrapper for click applications.
"""
import click

from .defaults import MELVEC_LENGTH, N_MELVECS

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
