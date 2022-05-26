import os
import requests
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from psycopg2 import IntegrityError

from forms import SignupForm, LoginForm, SearchForm, EditProfileForm
from models import  db, connect_db, User,  Instrument, Genre, Follows, User_Instrument, User_Genre
from flask_uploads import configure_uploads, IMAGES, UploadSet
from werkzeug.utils import secure_filename
import uuid as uuid
from sqlalchemy import exc

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///hook-find-musicians'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

BASE_DIRECTORY = 'http://127.0.0.1:5000/'
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

toolbar = DebugToolbarExtension(app)

connect_db(app)


filename = 'apikey.txt'


def get_file_contents(filename):
    """Get contents of a file"""
    try:
        with open(filename, 'r') as f:
            # It's assumed our file contains a single line,
            # with our API key
            return f.read().strip()
    except FileNotFoundError:
        print("'%s' file not found" % filename)


API_KEY = get_file_contents(filename)
RADIUS_BASE_URL = f'https://www.zipcodeapi.com/rest/{API_KEY}/radius.json'


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in the user."""
    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out the user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def home_page():
    """Render home page. """

    if not g.user:
        return render_template('home-anon.html')
    else:    
        return redirect('/search')



@app.route('/login', methods=['GET','POST'])
def login_form():
    """Render login form page. """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "info")
            return redirect("/")

        flash("Invalid credentials.", 'danger')
    
    return render_template('/auth.html', form=form, page='Login')

        
@app.route('/logout')
def logout():
    """Log user out and redirect to login."""

    do_logout()
    flash('Successfully logged out.','info')

    return redirect('/')


@app.route('/signup', methods=['GET','POST'])
def signup_form():
    """Render signup form page. """

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data, 
                email=form.email.data, 
                password=form.password.data, 
                city=form.city.data, 
                state=form.state.data, 
                zip_code=form.zip_code.data, 
                is_band=form.is_band.data,
                header_image=User.header_image.default.arg,
                profile_image=User.profile_image.default.arg
            )
            db.session.commit();
        
        except exc.IntegrityError:
            db.session.rollback()
            flash('Username or Email already taken', 'danger')
            return render_template('auth.html', form=form, page='Signup')

        do_login(user)

        return redirect('/')

    else: 
        return render_template('auth.html', form=form, page='Signup')


@app.route('/search', methods=['GET','POST'])
def search_musicians():
    """Render search form page."""

    if not g.user:
        return render_template('home-anon.html')

    form=SearchForm()   
    if form.validate_on_submit():

        session["searching_for_band"] = form.is_band.data
        session["searching_instrument"] = form.instruments.data
        session["searching_genre"] = form.genres.data
        zip = form.zip_code.data
        radius = form.radius.data

        resp = requests.get(f"{RADIUS_BASE_URL}/{zip}/{radius}/miles")

        res = resp.json()['zip_codes']

        zips = []

        for zip in res:
            zips.append(zip['zip_code'])

        session['response_zip_codes'] = zips

        return redirect ('/results')

    else:
        return render_template('search.html', form=form, page='search')

    


@app.route('/results')
def search_results():
    """Display search results on the page"""
    
    if not g.user:
        return render_template('home-anon.html')

    instrument = Instrument.query.filter_by(name = session["searching_instrument"]).one()
    genre = Genre.query.filter_by(name = session["searching_genre"]).one()

    users = db.session.query(User).filter(
        User.zip_code.in_(session["response_zip_codes"]),
        User.is_band == session["searching_for_band"], 
        User.instruments.any(Instrument.id == instrument.id),
        User.genres.any(Genre.id == genre.id))
    
    return render_template('search-results.html', users=users, page='search')



@app.route('/users/<int:user_id>')
def user_profile(user_id):
    """Render a user's profile"""

    if not g.user:
        return render_template('home-anon.html')

    user = User.query.get_or_404(user_id)
    curr_user = g.user

    return render_template('profile.html', user=user,curr_user=curr_user, page='profile')


@app.route('/users/edit', methods=['GET','POST'])
def edit_user_profile():
    """Render form to edit current user's profile. Submit form and redirect to profile page"""
 
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/users/{g.user.id}")

    form = EditProfileForm(obj=g.user)
    
    if form.validate_on_submit():
        
        user = User.authenticate(g.user.username,form.password.data)

        if user:
            
            # Upload header image
            if request.files['header_image']:
                
                updated_header_img = request.files['header_image']
                
                # Grab Image Names
                header_img_filename = secure_filename(updated_header_img.filename)
                
                # Set UUID
                header_img_uuid_name = str(uuid.uuid1()) + "_" + header_img_filename

                #Save Images
                updated_header_img.save(os.path.join(app.config['UPLOAD_FOLDER'],header_img_uuid_name))

                #Change it to a string to save to db
                header_img_filename = BASE_DIRECTORY + UPLOAD_FOLDER + header_img_uuid_name

                g.user.header_image =  header_img_filename or User.header_image.default.arg
            

            # Upload profile image
            if request.files['profile_image']:

                updated_profile_img = request.files['profile_image'] 
                
                # Grab Image Names
                profile_img_filename = secure_filename(updated_profile_img.filename)

                # Set UUID
                profile_img_uuid_name = str(uuid.uuid1()) + "_" + profile_img_filename

                #Save Images
                updated_profile_img.save(os.path.join(app.config['UPLOAD_FOLDER'],profile_img_uuid_name))

                #Change it to a string to save to db
                profile_img_filename = BASE_DIRECTORY +UPLOAD_FOLDER + profile_img_uuid_name

                g.user.profile_image = profile_img_filename or User.profile_image.default.arg


            # Update username, email, and bio from form data
            g.user.username = form.username.data
            g.user.email = form.email.data
            g.user.bio = form.bio.data
            
            # Clear current user's instruments list before adding form data
            g.user.instruments = []

            # Add form data to add instruments to current user's list
            for instrument in form.instruments.data:

                inst = Instrument.query.filter_by(name = instrument).one()
                User_Instrument.add_instrument_to_user(user_id=user.id, instrument_id=inst.id)
                db.session.add(inst)

            # Clear current user's genres list before adding form data
            g.user.genres = []

            # Add form data to add instruments to current user's list
            for genre in form.genres.data:
    
                gen = Genre.query.filter_by(name = genre).one()
                User_Genre.add_genre_to_user(user_id=user.id, genre_id=gen.id)
                db.session.add(gen)
            
            db.session.commit()

            print(form.errors)
            flash('Successfully updated profile.', 'success')
            return redirect(f"/users/{user.id}")
        
        flash("You entered the wrong password!","error")
        return redirect(request.url)
    else:
        # Update form fields with user data for instruments and genres
        form.instruments.data = [instrument.name for instrument in g.user.instruments]
        form.genres.data = [genre.name for genre in g.user.genres]
        
        print(form.errors)
        return render_template('edit.html', form=form, page='profile',user=g.user)
