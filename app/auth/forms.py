from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    username = StringField(
        "Имя пользователя",
        validators=[DataRequired(), Length(min=3, max=64)],
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired(), Length(min=6, max=128)],
    )
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Имя пользователя",
        validators=[DataRequired(), Length(min=3, max=64)],
    )
    email = StringField(
        "Электронная почта",
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired(), Length(min=6, max=128)],
    )
    password2 = PasswordField(
        "Повторите пароль",
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField("Создать аккаунт")

    def validate_username(self, username: StringField) -> None:
        if User.query.filter_by(username=username.data.strip()).first():
            raise ValidationError("Пользователь с таким именем уже существует.")

    def validate_email(self, email: StringField) -> None:
        if User.query.filter_by(email=email.data.strip().lower()).first():
            raise ValidationError("Пользователь с таким email уже существует.")
