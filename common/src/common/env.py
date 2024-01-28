"""Utilities for loading environ variables easily."""
from pathlib import Path

import dotenv

repository_dir = Path(__file__).parents[3]


def load_dotenv() -> None:
    """
    Load .env file from repository's root directory,
    if present.
    """
    dotenv_path = repository_dir / ".env"

    if dotenv_path.exists():
        dotenv.load_dotenv(dotenv_path=dotenv_path)
