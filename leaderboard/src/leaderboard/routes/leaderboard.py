import urllib

import flask
from ..backend.models import Guess, Submission
from flask import Blueprint
from flask import current_app as app
from flask import jsonify, make_response, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restx import Api, Resource

leaderboard = Blueprint("leaderboard", __name__, static_folder="../static")

api = Api(
    leaderboard,
    title="Leaderboard API",
    description="The API documentation. Please click on **default** to show all the possible endpoints.",
    doc="/doc/",
)

limiter = Limiter(
    get_remote_address,
    storage_uri="memory://",
)


@api.route("/security/<path:key>/<path:guess>/<path:traces>", methods=["POST"])
@api.param("key", "Your key")
@api.param("guess", "Your guess")
@api.param("traces", "The number of traces your measured")
class Security(Resource):
    """
    Submits a guess for the security round.
    """

    # https://stackoverflow.com/questions/60369112/flask-limiter-does-not-work-with-flask-restful-api-based-application
    decorators = [limiter.limit("30 per minute")]

    def post(self, key, guess, traces):
        try:
            app.config["CONFIG"].get_group_by_key(key)  # IndexError if invalid key
            guess_bytes = urllib.parse.unquote_to_bytes(guess)
            traces_int = int(traces)

            app.config["CONFIG"].rounds_config.add_security_round_submission(
                key, guess_bytes, traces_int
            )
            return make_response(
                jsonify(
                    {
                        "guess": guess,
                        "traces": traces,
                    }
                ),
                200,
            )
        except IndexError:
            return make_response(
                jsonify(
                    {
                        "error": "the provided key does not match any group name",
                        "key": key,
                    }
                ),
                401,
            )
        except IndexError:
            return make_response(
                jsonify(
                    {
                        "error": "traces could not be parse into an integer",
                        "traces": traces,
                    }
                ),
                401,
            )
        except:
            return make_response(
                jsonify(
                    {
                        "error": "the provided guess cannot be properly decoded using base64.b64decode",
                        "guess": guess,
                    }
                ),
                401,
            )


@api.route("/submit/<path:key>/<path:guess>", methods=["POST"])
@api.param("key", "Your key")
@api.param("guess", "Your guess")
class Submit(Resource):
    """
    Submits a guess to current round and current lap.
    """

    def dispatch_request(self, key, guess):
        try:
            guess = Guess[guess.lower()]  # KeyError if invalid answer
            app.config["CONFIG"].get_group_by_key(key)  # IndexError if invalid key

            rounds_config = app.config["CONFIG"].rounds_config
            current_round = rounds_config.get_current_round()
            current_lap = rounds_config.get_current_lap()
            penalized = not rounds_config.accepts_submissions()

            if not rounds_config.is_paused():
                rounds_config.add_submission(
                    Submission(
                        round=current_round,
                        lap=current_lap,
                        key=key,
                        guess=guess,
                        penalized=penalized,
                    )
                )
                return make_response(
                    jsonify(
                        {
                            "guess": guess,
                            "round": current_round,
                            "lap": current_lap,
                            "penalized": penalized,
                        }
                    ),
                    200,
                )

            return make_response(
                jsonify(
                    {
                        "error": "no submissions are allowed, please wait for a new round to start"
                    }
                ),
                400,
            )
        except IndexError:
            return make_response(
                jsonify(
                    {
                        "error": "the provided key does not match any group name",
                        "key": key,
                    }
                ),
                401,
            )
        except KeyError:
            return make_response(
                jsonify(
                    {
                        "error": "the provided guess does not exist",
                        "guess": guess.lower(),
                        "possible-values": Guess.possible_values(),
                    }
                ),
                400,
            )

    @api.response(200, "Success")
    @api.response(400, "Submissions currently not allowed")
    @api.response(401, "Invalid key")
    def post(self, key, guess, patch=False):
        """Submit a guess to current round and current lap."""

    @api.response(200, "Success")
    @api.response(400, "Submissions currently not allowed")
    @api.response(401, "Invalid key")
    def patch(self, key, guess):
        """
        Changes the last guess of current round and current lap.

        If not guesses were made, this is equivalent to the POST method.
        """


@api.route(
    "/submissions/<path:key>",
    methods=["GET", "DELETE"],
    defaults={"round": None, "lap": None},
)
@api.route(
    "/submissions/<path:key>/<path:round>",
    methods=["GET", "DELETE"],
    defaults={"round": None},
)
@api.route("/submissions/<path:key>/<path:round>/<path:lap>", methods=["GET", "DELETE"])
@api.param("key", "Your key")
@api.param(
    "round", "The round from which submissions are taken", type=int, required=False
)
@api.param("lap", "The lap from which submissions are taken", type=int, required=False)
class Submissions(Resource):
    """
    Manipulates submissions, with optinal valeus for round and lap numbers.

    If GET, returns the list of submissions.

    If DELETE, deletes the submissions.
    """

    def dispatch_request(self, key, round, lap):
        try:
            app.config["CONFIG"].get_group_by_key(key)  # IndexError if invalid key
            rounds_config = app.config["CONFIG"].rounds_config

            if flask.request.method == "GET":
                submissions = rounds_config.get_submissions_as_dict(
                    key=key, round=round, lap=lap
                )
                return make_response(
                    jsonify(
                        {
                            "method": flask.request.method,
                            "round": round,
                            "lap": lap,
                            "submissions": submissions,
                        }
                    ),
                    200,
                )
            elif flask.request.method == "DELETE":
                rounds_config.delete_submissions(key=key, round=round, lap=lap)
                return make_response(
                    jsonify(
                        {"method": flask.request.method, "round": round, "lap": lap}
                    ),
                    200,
                )
            else:
                raise ValueError(f"Unsupported method type: {flask.request.method}")
        except IndexError:
            return make_response(
                jsonify(
                    {
                        "error": "the provided key does not match any group name",
                        "key": key,
                    }
                ),
                401,
            )

    @api.response(200, "Success")
    @api.response(401, "Invalid key")
    def get(self, key, round, lap):
        """Returns all submissions from a given group."""

    @api.response(200, "Success")
    @api.response(401, "Invalid key")
    def delete(self, key, round, lap):
        """Returns all submissions from a given group."""


@api.route("/check/<path:key>", methods=["GET"])
@api.param("key", "Your key")
class Get(Resource):
    @api.response(200, "Success")
    @api.response(401, "Invalid key")
    def get(self, key):
        """
        Checks wether a key is valid of not.
        """
        try:
            response = app.config["CONFIG"].get_group_by_key(key).dict()
            del response["key"]
            return make_response(jsonify(response), 200)
        except IndexError:
            return make_response(
                jsonify(
                    {
                        "error": "the provided key does not match any group name",
                        "key": key,
                    }
                ),
                401,
            )


@api.route("/status/", methods=["GET"], defaults={"key": None})
@api.route(
    "/status/<path:key>",
    methods=["GET"],
)
@api.param("key", "Your key, only admin allowed", required=False)
class Status(Resource):
    @api.response(200, "Success")
    @api.response(401, "Invalid key")
    @api.response(403, "Unauthorized user")
    def get(self, key):
        """
        Returns the current status of the leaderboard.
        """
        try:
            leaderboard_status = app.config["CONFIG"].get_leaderboard_status().dict()
            del leaderboard_status["leaderboard"]

            if key:
                if not app.config["CONFIG"].get_group_by_key(key).admin:
                    return make_response(
                        jsonify({"error": "the provided key has no admin rights"}), 403
                    )
            else:
                del leaderboard_status["current_correct_guess"]
                del leaderboard_status["time_before_playing"]

            return make_response(
                jsonify(leaderboard_status),
                200,
            )
        except IndexError:
            return make_response(
                jsonify(
                    {
                        "error": "the provided key does not match any group name",
                        "key": key,
                    }
                ),
                401,
            )


@api.route(
    "/play/<path:key>",
    methods=["POST"],
)
@api.param("key", "Your key, only admin allowed")
class Play(Resource):
    @api.response(200, "Success")
    @api.response(401, "Invalid key")
    @api.response(403, "Unauthorized user")
    def post(self, key):
        """
        Plays the rounds.
        """
        try:
            if not app.config["CONFIG"].get_group_by_key(key).admin:
                return make_response(
                    jsonify({"error": "the provided key has no admin rights"}), 403
                )

            app.config["CONFIG"].rounds_config.play()

            return make_response(
                jsonify({"status": "playing"}),
                200,
            )
        except IndexError:
            return make_response(
                jsonify(
                    {
                        "error": "the provided key does not match any group name",
                        "key": key,
                    }
                ),
                401,
            )


@api.route(
    "/pause/<path:key>",
    methods=["POST"],
)
@api.param("key", "Your key, only admin allowed")
class Pause(Resource):
    @api.response(200, "Success")
    @api.response(401, "Invalid key")
    @api.response(403, "Unauthorized user")
    def post(self, key):
        """
        Pauses the rounds.
        """
        try:
            if not app.config["CONFIG"].get_group_by_key(key).admin:
                return make_response(
                    jsonify({"error": "the provided key has no admin rights"}), 403
                )

            app.config["CONFIG"].rounds_config.pause()

            return make_response(
                jsonify({"status": "paused"}),
                200,
            )
        except IndexError:
            return make_response(
                jsonify(
                    {
                        "error": "the provided key does not match any group name",
                        "key": key,
                    }
                ),
                401,
            )


@api.route(
    "/restart/<path:key>",
    methods=["POST"],
)
@api.param("key", "Your key, only admin allowed")
class Restart(Resource):
    @api.response(200, "Success")
    @api.response(401, "Invalid key")
    @api.response(403, "Unauthorized user")
    def post(self, key):
        """
        Restarts the rounds.
        """
        try:
            if not app.config["CONFIG"].get_group_by_key(key).admin:
                return make_response(
                    jsonify({"error": "the provided key has no admin rights"}), 403
                )

            app.config["CONFIG"].rounds_config.restart()

            return make_response(
                jsonify({"status": "restarted"}),
                200,
            )
        except IndexError:
            return make_response(
                jsonify(
                    {
                        "error": "the provided key does not match any group name",
                        "key": key,
                    }
                ),
                401,
            )


@api.route("/list/", methods=["GET"])
class List(Resource):
    def get(self):
        """
        Lists all possible guesses.
        """
        return make_response(
            jsonify(Guess.possible_values()),
            200,
        )


@api.route("/rename/<path:key>/<path:name>", methods=["PATCH"])
@api.param("key", "Your key")
@api.param("name", "Your new group name")
class Rename(Resource):
    @api.response(200, "Success")
    @api.response(400, "Name already exists")
    @api.response(401, "Invalid key")
    def patch(self, key, name):
        """
        Rename a group.
        """
        try:
            group_conf = app.config["CONFIG"].get_group_by_key(key)

            try:
                _ = app.config["CONFIG"].get_group_by_name(name)
                return make_response(
                    jsonify(
                        {
                            "error": "the provided name already exists",
                            "name": name,
                        }
                    ),
                    400,
                )
            except IndexError:
                pass

            group_conf.name = name
            app.config["CONFIG_NEEDS_SAVE"] = True

            return make_response(jsonify({"name": name}), 200)
        except IndexError:
            return make_response(
                jsonify(
                    {
                        "error": "the provided key does not match any group name",
                        "key": key,
                    }
                ),
                401,
            )


@api.route("", doc=False)
@api.route("/index", doc=False)
class Index(Resource):
    def get(self):
        headers = {"Content-Type": "text/html"}
        return make_response(render_template("leaderboard.html"), 200, headers)
