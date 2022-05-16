import email

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Optional


class SignupForm(FlaskForm):
    """Form for adding new users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[Email(),DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    zip_code = StringField('Zip Code', validators=[Length(min=5,max=5,message='Please enter a valid zip code.')])
    is_band = BooleanField('Is this a band page?')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])