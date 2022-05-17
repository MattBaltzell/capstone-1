import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from psycopg2 import IntegrityError

from forms import SignupForm, LoginForm
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
        return render_template('home.html')



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
                image_url=User.image_url.default.arg
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