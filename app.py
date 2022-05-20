import os
import requests
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from psycopg2 import IntegrityError

from forms import SignupForm, LoginForm, SearchForm
from models import db, connect_db, User, Post, Instrument, Genre, Song, Likes, Follows
from sqlalchemy import exc

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///hook-find-musicians'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
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
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('/auth.html', form=form, page='Login')

        
@app.route('/logout')
def logout():
    """Log user out and redirect to login."""

    do_logout()
    flash('Successfully logged out.')

    return redirect('/login')


@app.route('/signup', methods=['GET','POST'])
def signup_form():
    """Render signup form page. """

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data, 
                email=form.username.data, 
                password=form.password.data, 
                zip_code=form.zip_code.data, 
                is_band=form.is_band.data,
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

    form=SearchForm()   
    if form.validate_on_submit():

        session["searching_for_band"] = form.is_band.data
        zip = form.zip_code.data
        radius = form.radius.data

        resp = requests.get(f"{RADIUS_BASE_URL}/{zip}/{radius}/miles")

        res = resp.json()['zip_codes']

        zips = []
        zips_all = []

        for zip in res:
            zips.append(zip['zip_code'])
            zips_all.append(zip)

        session['response_zip_codes'] = zips

        print('=====================================')
        print(zips_all)
        print('=====================================')
        print('=====================================')
        
        return redirect ('/results')

    else:
        return render_template('search.html', form=form, page='search')

    


@app.route('/results')
def search_results():
    """Display search results on the page"""
    
    users = User.query.filter(User.zip_code.in_(session["response_zip_codes"]),User.is_band == session["searching_for_band"])
    
    return render_template('search-results.html', users=users, page='search')



@app.route('/users/<int:user_id>')
def user_profile(user_id):
    """Render a user's profile"""

    user = User.query.get_or_404(user_id)

    return render_template('profile.html', user=user,page='profile')