from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError
from application.models.user import User
from application import db


class AdminEditNoteForm(FlaskForm):
    title = StringField('Title', validators=[Length(min=1, max=150)])
    description = TextAreaField('Description', validators=[Length(min=1, max=150)], render_kw={"rows": 4})
    attachment = FileField('File')
    submit = SubmitField('Submit')

class AdminEditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=40)])
    email = StringField('Email Address', validators=[Length(min=6, max=35), DataRequired(), Email()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=150)])
    is_admin = BooleanField('Is administrator', validators=[])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(AdminEditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self,username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('This name is already being used')

class AdminPostForm(FlaskForm):
    title = StringField('Title', validators=[Length(min=1, max=150)])
    content = TextAreaField('Content', validators=[Length(min=1, max=150)], render_kw={"rows": 4})
    submit = SubmitField('Submit')

