from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        
# Define LoginForm
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AddListForm(FlaskForm):
    name = StringField('List Name', validators=[DataRequired()])
    submit = SubmitField('Create List')

class AddTaskForm(FlaskForm):
    task_name = StringField('Task Name', validators=[DataRequired()])
    submit = SubmitField('Add Task')

class AddSubtaskForm(FlaskForm):
    title = StringField('Subtask Title', validators=[DataRequired()])
    submit = SubmitField('Add Subtask')