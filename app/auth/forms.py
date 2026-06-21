from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign in")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    password2 = PasswordField(
        "Repeat password",
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField("Create account")

    def validate_username(self, username: StringField) -> None:
        if User.query.filter_by(username=username.data.strip()).first():
            raise ValidationError("Пользователь с таким именем уже существует.")
