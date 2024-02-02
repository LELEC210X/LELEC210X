import os
import time
import webbrowser
from pathlib import Path
from threading import Timer

import click
import eventlet
import markdown
import requests
from flask import Flask
from flask.cli import FlaskGroup, load_dotenv
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO

from common.click import verbosity
from common.logging import logger

from .backend.models import DEFAULT_CONFIG_PATH, Config
from .cli.config import config
from .play_sound import play_sound
from .routes.index import index
from .routes.leaderboard import leaderboard, limiter
from .submit import submit
from .utils import get_url

eventlet.monkey_patch(thread=True, time=True)

load_dotenv((Path(__file__).parents[2] / ".flaskenv").resolve(strict=True))


class PrefixMiddleware:
    def __init__(self, app, prefix=""):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ["PATH_INFO"].startswith(self.prefix):
            environ["PATH_INFO"] = environ["PATH_INFO"][len(self.prefix) :]
            environ["SCRIPT_NAME"] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response("404", [("Content-Type", "text/plain")])
            return [b"This url does not belong to the app."]


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.logger = logger

    if app.debug and os.environ.get("FLASK_PROFILER", "0") == "1":
        from werkzeug.middleware.profiler import ProfilerMiddleware

        if not os.path.exists("profiler"):
            os.mkdir("profiler")

        app.config["PROFILE"] = True
        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app,
            restrictions=[30],
            profile_dir="profiler",
            filename_format="{method}-{path}-{time:.0f}-{elapsed:.0f}ms.prof",
        )
    app.wsgi_app = PrefixMiddleware(
        app.wsgi_app, prefix=os.environ["FLASK_STATIC_PATH"]
    )

    config_path = app.config.get("CONFIG_PATH", DEFAULT_CONFIG_PATH)
    try:
        app.config["CONFIG"] = Config.parse_file(config_path)
    except FileNotFoundError:
        logger.warn(
            f"No config file found at '{config_path}', using default config values."
        )
        app.config["CONFIG"] = Config()

    app.config["CONFIG_PATH"] = config_path
    app.config["CONFIG_NEEDS_SAVE"] = False
    app.config["LIMITER"] = limiter

    app.config["SCHEDULER_API_ENABLE"] = True

    with app.app_context():
        app.config["CONFIG"].rounds_config.restart()

    scheduler = APScheduler()
    scheduler.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(index, url_prefix="/index")
    app.register_blueprint(leaderboard, url_prefix="/leaderboard")

    @app.route("/")
    def _index():
        readme_file = open("README.md")
        md_template_string = markdown.markdown(
            readme_file.read(), extensions=["fenced_code"]
        )

        return md_template_string

    socketio_kwargs = {
        "async_mode": "eventlet",
        "logger": logger,
    }

    if os.environ["FLASK_RUN_HOST"].lower() == "localhost":
        socketio = SocketIO(
            app,
            **socketio_kwargs,
        )

    else:
        socketio = SocketIO(
            app,
            cors_allowed_origins=os.environ["FLASK_RUN_HOST"],
            path=os.environ["FLASK_STATIC_PATH"] + "/socket.io/",
            **socketio_kwargs,
        )

    @socketio.on("connect")
    @scheduler.task("interval", id="update_client", seconds=1.0)
    def update_leaderboard():
        """Updates periodically the leaderboard by fetching data from the submissions."""
        with app.app_context():
            socketio.emit(
                "update_leaderboard",
                app.config["CONFIG"].get_leaderboard_status().dict(),
            )

    @scheduler.task("interval", id="save_config", seconds=5.0)
    def save_config():
        """Saves periodically the config, if needed."""
        with app.app_context():
            if app.config["CONFIG_NEEDS_SAVE"]:
                app.config["CONFIG"].save_to(app.config["CONFIG_PATH"])
                app.config["CONFIG_NEEDS_SAVE"] = False

    return app


@click.group(cls=FlaskGroup, create_app=create_app)
@verbosity
def main():
    pass


@main.command()
def ping():
    """Ping the leaderboard server and return round-trip time in ms."""
    url = f"{get_url()}/lelec210x/leaderboard/status"

    while True:
        t = time.time()
        response = requests.get(url)
        elapsed = 1000 * (time.time() - t)
        click.echo(f"[{response.status_code}] Took {elapsed:.2f} milliseconds")
        time.sleep(0.5)


@main.command()
@click.option(
    "--open",
    "_open",
    is_flag=True,
    help="Open landing page in a web browser, only when serving on localhost.",
)
@click.option(
    "--open-doc",
    "_open_doc",
    is_flag=True,
    help="Open documentation page in a web browser, only when serving on localhost.",
)
def serve(_open, _open_doc):
    """Run a leaderboard server."""
    app = create_app()

    if len(app.config["CONFIG"].group_configs) == 0:
        raise ValueError("Cannot run server without at least one group, see README.md.")

    app.apscheduler.start()
    host = os.environ["FLASK_RUN_HOST"].lower()
    port = os.environ["FLASK_RUN_PORT"]

    if _open and host == "localhost":
        Timer(
            1, lambda: webbrowser.open(f"http://{host}:{port}/lelec210x/leaderboard")
        ).start()

    if _open_doc and host == "localhost":
        Timer(
            1,
            lambda: webbrowser.open(f"http://{host}:{port}/lelec210x/leaderboard/doc"),
        ).start()

    app.extensions["socketio"].run(app, host=host, port=port)


main.add_command(config)
main.add_command(play_sound)
main.add_command(submit)

del main.commands["run"]

if __name__ == "__main__":
    main()
