from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class PhotoForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField("Описание")
    tags = StringField('Теги (через запятую)')
    photo = FileField('Фотография', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')
    ])
    is_private = BooleanField("Приватное")
    submit = SubmitField('Загрузить')