from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError
import re
from application.models.user import User
from application import db

ALLOWED_NOTE_EXTENSIONS = ['pdf', 'doc', 'txt']

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=4, max=25), DataRequired()])
    email = StringField('Email Address', validators=[Length(min=6, max=35), DataRequired(), Email()])
    password = PasswordField('New Password', 
        validators=[DataRequired(), Length(min=1)])
    confirm_password = PasswordField('Repeat Password', validators=
    [DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('This username is already taken')
    
    def validate_password(self, field):
        if not re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{8,}$", field.data):
            raise ValidationError('Password is too weak, password must contain at least one digit, one uppercase letter, one lowercase letter and one special character(@,#,$).')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("This e-mail address is already being used. If it\'s your address, try to reset your password.")

class NoteForm(FlaskForm):
    title = StringField('Title', validators=[Length(min=1, max=150)])
    description = TextAreaField('Description', validators=[Length(min=1, max=150)], render_kw={"rows": 4})
    attachment = FileField('File')
    submit = SubmitField('Submit')

    def validate_attachment(self, field):
        if request.files:
            if request.files[self.attachment.name]:
                if request.files[self.attachment.name].filename.split('.')[-1] not in ALLOWED_NOTE_EXTENSIONS:
                    raise ValidationError('Extension not supported.')

class PasswordChangeForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(), Length(min=1)])
    confirm_new_password = PasswordField('Repeat Password', validators=
    [DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Confirm')

    def validate_new_password(self,field):
        if not re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{8,}$", field.data):
            raise ValidationError('Password is too weak, password must contain at least one digit, one uppercase letter, one lowercase letter and one special character(@,#,$).')
        
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=40)])
    photo = FileField('Profile pic')
    about_me = TextAreaField('About me', validators=[Length(min=0, max=300)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self,username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('This name is already being used')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=1)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Submit')

    def validate_password(self, field):
        if not re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{8,}$", field.data):
            raise ValidationError('Password is too weak, password must contain at least one digit, one uppercase letter, one lowercase letter and one special character(@,#,$).')
    
