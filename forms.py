import email
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from multiselect_options import INSTRUMENT_CHOICES, GENRE_CHOICES
from models import Instrument, Genre
from wtforms import StringField, IntegerField, PasswordField, BooleanField, IntegerRangeField, RadioField, TextAreaField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange


class SignupForm(FlaskForm):
    """Form for adding new users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[Email(),DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[Length(min=2,max=2,message='Use abbreviated state name (AL, CA, NY, TX).'),DataRequired()])
    zip_code = IntegerField('Zip Code', validators=[NumberRange(min=00000, max=99999, message='Please enter a valid zip code.'),DataRequired()])
    is_band = BooleanField('Is this a band page?')


def create_multiform_choices(list):
    """Create choice tuples to use as multiform choices."""

    result = []
   
    for choice in list:
        try:
            result.append((choice, choice.title()))
        except:pass
    return result

instrument_choices = create_multiform_choices(INSTRUMENT_CHOICES)
genre_choices = create_multiform_choices(GENRE_CHOICES)


class EditProfileForm(FlaskForm):
    """Form for editing logged-in user's profile"""

    header_image = FileField('Header Image')
    profile_image = FileField('Profile Image')
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[Email(),DataRequired()])
    city = StringField('City', validators=[Length(min=2),DataRequired()])
    state = StringField('State', validators=[Length(min=2,max=2,message='Please abbreviate the state (e.g. WA, CA, NY).'),DataRequired()])
    zip_code = IntegerField('Zip Code', validators=[NumberRange(min=00000, max=99999, message='Please enter a valid zip code.'),DataRequired()])
    instruments = SelectMultipleField('Instruments', id='instruments', choices=instrument_choices)
    genres = SelectMultipleField('Genres', id='genres', choices=genre_choices)
    bio = TextAreaField('Bio',render_kw={"rows": 5, "cols": 11})
    password = PasswordField('Password', validators=[Length(min=6)])


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
    instruments = SelectField('Instrument Played', id='instruments-search', choices=instrument_choices)
    genres = SelectField('Genre Played', id='genres-search', choices=genre_choices)
    zip_code = IntegerField('Zip Code', validators=[NumberRange(min=00000, max=99999, message='Please enter a valid zip code.'),DataRequired()])
    radius = IntegerRangeField('Radius in Miles', default=10)


class MessageForm(FlaskForm):
    """Form for sending message to another user."""

    subject = StringField()
    body = TextAreaField(('Message'), validators=[
        DataRequired(), Length(min=0, max=140)])
    
class PasswordUpdateForm(FlaskForm):
    """Form for updating current user's password"""

    old_password = PasswordField('Enter Old Password', validators=[Length(min=6)])
    new_password = PasswordField('Enter New Password', validators=[Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[Length(min=6)])