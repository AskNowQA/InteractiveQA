from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms.validators import InputRequired


class SubmitQuestionForm(FlaskForm):
    question = StringField(id='question', label='Question: ', validators=[InputRequired()])
    task = HiddenField(id='task')
