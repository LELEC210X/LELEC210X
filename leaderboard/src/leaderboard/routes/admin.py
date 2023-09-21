from flask import redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from forms import GroupNamesForm, LoginForm, ResetForm, RoundConfigForm
from models import User
from my_app import app, round_config, socketio


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin"))

    login_form = LoginForm()
    if login_form.login_submit.data and login_form.validate():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and user.check_password_hash(login_form.password.data):
            login_user(user)
            return redirect(url_for("admin"))

    return render_template("login.html", login_form=login_form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    reset_form = ResetForm()

    if reset_form.reset_submit.data and reset_form.validate():
        round_config.reset()

    group_names_form = GroupNamesForm()
    if group_names_form.group_names_submit.data and group_names_form.validate():
        round_config.group_names = group_names_form.group_names.data

    round_config_form = RoundConfigForm()

    if round_config_form.round_config_submit.data and round_config_form.validate():
        round_config.current_round = round_config_form.current_round.data
        round_config.lap_timings = round_config_form.lap_timings_rle.data
        round_config.gt_answers = round_config_form.gt_answers.data
        round_config.check_class = round_config_form.check_class.data

    return render_template(
        "admin.html",
        reset_form=reset_form,
        group_names_form=group_names_form,
        round_config_form=round_config_form,
        round_config=round_config,
    )


@app.route("/launch", methods=["GET", "POST"])
@login_required
def launch():
    round_config.launch()
    socketio.emit("get_client_state", round_config.get_client_state())
    return ""
