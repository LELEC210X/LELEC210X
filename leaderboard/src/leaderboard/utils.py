import os


def get_url() -> str:
    """Return the leaderboard base url from preloaded environ variables."""
    host = os.environ["FLASK_RUN_HOST"].lower()
    port = os.environ["FLASK_RUN_PORT"] or "5000"

    if host in {"localhost", "0.0.0.0"}:
        return f"http://{host}:{port}"

    return f"https://{host}"
