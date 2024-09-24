import secrets
from pathlib import Path

import click

from ..backend.models import DEFAULT_CONFIG_PATH, Config, GroupConfig, RoundsConfig


@click.group()
@click.help_option("-h", "--help")
def config():
    """Performs operations on the config."""


@config.command()
@click.option(
    "-c",
    "--config",
    "config_path",
    default=DEFAULT_CONFIG_PATH,
    type=click.Path(dir_okay=False),
    help="JSON file where the config is saved.",
    show_default=True,
)
@click.option(
    "-f", "--force", is_flag=True, help="If set, will overwrite any existing config."
)
def init(config_path: Path, force: bool) -> None:
    """Initialize a new config."""
    if config_path.exists() and not force:
        raise click.UsageError(
            f"Config file `{config_path}` already exists. Use `--force` to overwrite."
        )
    with open(config_path, "w") as f:
        f.write(Config().json(indent=2))


@config.command()
@click.argument("name")
@click.option(
    "-c",
    "--config",
    "config_path",
    default=DEFAULT_CONFIG_PATH,
    type=click.Path(dir_okay=False),
    help="JSON file where the config is saved.",
    show_default=True,
)
@click.option(
    "-s",
    "--size",
    default=30,
    type=click.IntRange(1, 128),
    help="Key size is bytes (1 byte ~ 1.3 characters).",
    show_default=True,
)
@click.option("--admin", is_flag=True, help="If set, the group will have admin rights.")
@click.option(
    "-f", "--force", is_flag=True, help="If set, will overwrite any existing key."
)
@click.help_option("-h", "--help")
def generate_key(
    name: str, config_path: Path, size: int, admin: bool, force: bool
) -> None:
    """Generate a key for a given group NAME."""
    if not config_path.exists():
        raise click.UsageError(
            f"config file `{config_path}` does not exist. "
            "Please create one first with `rye run leaderboard config init`"
        )

    config = Config.parse_file(config_path)

    key = secrets.token_urlsafe(size)

    try:
        group_config = config.get_group_by_name(name)
    except IndexError:
        group_config = None

    if group_config:
        if force:
            group_config.key = key
            group_config.admin = admin
        else:
            raise click.UsageError(
                f"group `{name}` already has a key in "
                f"`{config_path}`. Use `--force` to overwrite it"
            )
    else:
        config.group_configs.append(GroupConfig(name=name, key=key, admin=admin))

    click.echo(f"Group {name} now has key: {key}")

    config.save_to(config_path)


@config.command()
@click.option(
    "-c",
    "--config",
    "config_path",
    default=DEFAULT_CONFIG_PATH,
    type=click.Path(exists=True, dir_okay=False),
    help="JSON file where the config is saved.",
    show_default=True,
)
@click.help_option("-h", "--help")
def reset_rounds_config(config_path: Path) -> None:
    """Overwrite an existing config by resetting the rounds config to default."""
    config = Config.parse_file(config_path)
    config.rounds_config = RoundsConfig()
    config.save_to(config_path)
