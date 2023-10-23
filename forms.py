from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired
from datetime import datetime
from wtforms import ValidationError


class SignUpForm(FlaskForm):
    inputFirstName = StringField('First Name',
        [DataRequired(message="Please enter your first name!")])
    inputLastName = StringField('Last Name',
        [DataRequired(message="Please enter your last name!")])
    inputEmail = StringField('Email address',
        [Email(message="Not a valid email address!"),
        DataRequired(message="Please enter your email address!")])
    inputPassword = PasswordField('Password',
        [InputRequired(message="Please enter your password!"),
        EqualTo('inputConfirmPassword', message="Passwords does not match!")])
    inputConfirmPassword = PasswordField("Confirm password")
    submit = SubmitField('Sign Up')

class SignInForm(FlaskForm):
    inputEmail = StringField('Email address',
        [Email(message="Not a valid email address!"),
        DataRequired(message="Please enter your email address!")])
    inputPassword = PasswordField('Password',
        [InputRequired(message="Please enter your password!")])
    submit = SubmitField('Sign In')

class TaskForm(FlaskForm):

    inputDescription = StringField('Task Description',
        [DataRequired(message="Please enter your task content!")])
    inputDeadline = DateTimeLocalField('Deadline', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    def validate_inputDeadline(self, inputDeadline):
        if inputDeadline.data < datetime.now():
            raise ValidationError("Deadline cannot be in the past.")
        
         
    inputProject = SelectField('Project', coerce = int)
    inputStatus = SelectField('Status', coerce = int)
    inputPriority = SelectField('Priority', coerce = int)


    submit = SubmitField('Create Task')
    saveSubmit = SubmitField('Save')

class ProjectForm(FlaskForm):
    inputName = StringField('Project Name',
        [DataRequired(message="Please enter your project name!")])
    inputDescription = StringField('Project Description',
        [DataRequired(message="Please enter your project content!")])
    
    inputDeadline = DateTimeLocalField('Deadline', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    def validate_inputDeadline(self, inputDeadline):
        if inputDeadline.data < datetime.now():
            raise ValidationError("Deadline cannot be in the past.")
        
    inputStatus = SelectField('Status', coerce = int)

    submit = SubmitField('Create Project')
    saveSubmit = SubmitField('Save')