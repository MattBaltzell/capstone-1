import email

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerRangeField, RadioField
from wtforms.validators import DataRequired, Email, Length


class SignupForm(FlaskForm):
    """Form for adding new users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[Email(),DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    zip_code = StringField('Zip Code', validators=[Length(min=5,max=5,message='Please enter a valid zip code.')])
    is_band = BooleanField('Is this a band page?')

# class EditProfileForm(FlaskForm):
#     """Form for editing logged-in user's profile"""

#     username = StringField('Username', validators=[DataRequired()])
#     email = StringField('E-mail', validators=[Email(),DataRequired()])
#     city = StringField('City', validators=[Length(min=2),DataRequired()]))
#     state = StringField('State', validators=[Length(min=2,max=2,message='Please abbreviate the state (e.g. WA, CA, NY).'),DataRequired()])
#     zip_code = StringField('Zip Code', validators=[Length(min=5,max=5,message='Please enter a valid zip code.'),DataRequired()])
#     is_band = BooleanField('Is this a band page?', validators=[DataRequired()])



class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class SearchForm(FlaskForm):
    """Form for searching for other users within a radius"""

    is_band= RadioField('Profile Type', choices=[
    (False, 'Musicians'),
    (True, 'Bands')],
    default=False, validators=[DataRequired()])
    zip_code = StringField('Zip Code', validators=[Length(min=5,max=5,message='Please enter a valid zip code.')])
    radius = IntegerRangeField('Radius in Miles', default=10)