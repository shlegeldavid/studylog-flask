from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models import User


class PostForm(FlaskForm):
    body = TextAreaField(
        "Текст заметки",
        validators=[DataRequired(), Length(min=1, max=280)],
    )
    submit = SubmitField("Опубликовать")


class EditProfileForm(FlaskForm):
    username = StringField(
        "Имя пользователя",
        validators=[DataRequired(), Length(min=3, max=64)],
    )
    about_me = TextAreaField("О себе", validators=[Length(max=280)])
    submit = SubmitField("Сохранить")

    def __init__(self, original_username: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username: StringField) -> None:
        if username.data.strip() == self.original_username:
            return
        if User.query.filter_by(username=username.data.strip()).first():
            raise ValidationError("Это имя пользователя уже занято.")


class EmptyForm(FlaskForm):
    submit = SubmitField("Отправить")
