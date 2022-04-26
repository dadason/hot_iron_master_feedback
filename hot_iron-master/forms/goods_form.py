from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, HiddenField, SelectField
from wtforms.validators import DataRequired


class GoodsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Описание")
    category = SelectField("Категория", choices=[(1, 'Ворота'), (2, 'Двери'), (3, 'Решетки')], coerce=int, default=(2, 'Двери'))
    # photo = HiddenField("Фото")
    submit = SubmitField('Применить')
