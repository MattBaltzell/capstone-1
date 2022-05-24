import email

from flask_wtf import FlaskForm
from models import Instrument, Genre
from wtforms import StringField, PasswordField, BooleanField, IntegerRangeField, RadioField, TextAreaField, SelectMultipleField, FileField, SelectField
from wtforms.validators import DataRequired, Email, Length


class SignupForm(FlaskForm):
    """Form for adding new users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[Email(),DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[Length(min=2,max=2,message='Use abbreviated state name (AL, CA, NY, TX).'),DataRequired()])
    zip_code = StringField('Zip Code', validators=[Length(min=5,max=5,message='Please enter a valid zip code.')])
    is_band = BooleanField('Is this a band page?')

GENRE_CHOICES = "generator/genres.txt"
INSTRUMENT_CHOICES = "generator/instruments.txt"

def create_multiform_choices(choices_file):
    file = choices_file
    result = []
    with open(file, "r") as choices:
        for choice in choices.readlines():
            
            try:
                  result.append((choice.strip(), choice.strip().title()))
            except:pass
    return result

instrument_choices = create_multiform_choices(INSTRUMENT_CHOICES)
genre_choices = create_multiform_choices(GENRE_CHOICES)


class EditProfileForm(FlaskForm):
    """Form for editing logged-in user's profile"""

    header_image = FileField()
    profile_image = FileField()
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[Email(),DataRequired()])
    city = StringField('City', validators=[Length(min=2),DataRequired()])
    state = StringField('State', validators=[Length(min=2,max=2,message='Please abbreviate the state (e.g. WA, CA, NY).'),DataRequired()])
    zip_code = StringField('Zip Code', validators=[Length(min=5,max=5,message='Please enter a valid zip code.'),DataRequired()])
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

    zip_code = StringField('Zip Code', validators=[Length(min=5,max=5,message='Please enter a valid zip code.')])
    radius = IntegerRangeField('Radius in Miles', default=10)