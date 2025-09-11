from flask import Blueprint, render_template

index = Blueprint("index", __name__, static_folder="../static")


@index.route("/")
def _index():
    return render_template("index.html")
