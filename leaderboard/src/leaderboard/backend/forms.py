from converters import classes_to_id_dict
from flask_wtf import FlaskForm
from wtforms.fields import (
    IntegerField,
    PasswordField,
    RadioField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Regexp


class ResetForm(FlaskForm):
    reset_submit = SubmitField("Reset")


class GroupNamesForm(FlaskForm):
    group_names = TextAreaField("Group Names", validators=[DataRequired()])
    group_names_submit = SubmitField("Configure")


class RoundConfigForm(FlaskForm):
    current_round = IntegerField(
        "Current Round #", validators=[InputRequired(), NumberRange(min=0)]
    )

    classes_str = "|".join(classes_to_id_dict.keys())

    lap_timings_rle = TextAreaField(
        "RLE lap configuration",
        validators=[
            DataRequired(),
            Regexp("^[1-9][0-9]*,[1-9][0-9]*(,[1-9][0-9]*,[1-9][0-9]*)*$"),
        ],
    )
    gt_answers = TextAreaField(
        "Ground Truth Answers",
        validators=[DataRequired(), Regexp(f"^({classes_str})(,({classes_str}))*$")],
    )
    check_class = RadioField(
        "Check classes for the score",
        validators=[DataRequired()],
        choices=[("yes", "Yes"), ("no", "No")],
    )

    round_config_submit = SubmitField("Configure")


class LaunchRoundForm(FlaskForm):
    launch_round_submit = SubmitField("Launch")


class LoginForm(FlaskForm):
    username = StringField("username", validators=[Length(max=50)])
    password = PasswordField("password", validators=[Length(max=50)])
    login_submit = SubmitField("Login")
