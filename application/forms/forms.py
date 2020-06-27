from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError
import re
from database import db
from const import *

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=4, max=25), DataRequired()])
    email = StringField('Email Address', validators=[Length(min=6, max=35), DataRequired(), Email()])
    password = PasswordField('New Password', 
        validators=[DataRequired(), Length(min=1)])
    confirm = PasswordField('Repeat Password', validators=
    [DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

#    def validate_username(self, field):
#        if field.data in db.lrange(USERS, 0, -1):
#            raise ValidationError('This username is already taken')
    
    # def validate_password(self, field):
    #     if not re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{8,}$", field.data):
    #         raise ValidationError('Password is too weak, password must contain at least one digit, one uppercase letter, one lowercase letter and one special character(@,#,$).')


class NoteForm(FlaskForm):
    title = StringField('Title', validators=[Length(min=1, max=150)])
    description = TextAreaField('Description', validators=[Length(min=1, max=150)], render_kw={"rows": 1})
    submit = SubmitField('Post')

class PasswordChangeForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(), Length(min=1)])
    confirm_new_password = PasswordField('Repeat Password', validators=
    [DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Confirm')

    # def validate_new_password(self,field):
    #     if not re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{8,}$", field.data):
    #         raise ValidationError('Password is too weak, password must contain at least one digit, one uppercase letter, one lowercase letter and one special character(@,#,$).')
        
