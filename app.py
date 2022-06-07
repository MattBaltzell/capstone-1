import os
import requests
from flask import Flask, render_template, request, flash, redirect, session, g, url_for, send_from_directory, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from psycopg2 import IntegrityError
from datetime import datetime
from forms import SignupForm, LoginForm, SearchForm, EditProfileForm, MessageForm, PasswordUpdateForm
from models import  db, connect_db, User,  Instrument, Genre, Follows, User_Instrument, User_Genre, Message, Notification, bcrypt
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
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

POSTS_PER_PAGE = 10
app.config['POSTS_PER_PAGE']=POSTS_PER_PAGE
# toolbar = DebugToolbarExtension(app)

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

@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

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

    if g.user:
        return redirect(f'/users/{g.user.id}')

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,form.password.data)

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

    if g.user:
        return redirect(f'/users/{g.user.id}')

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
            flash('Username or Email already taken', 'danger')
            return render_template('auth.html', form=form, page='Signup')

        do_login(user)

        return redirect(f'/users/{user.id}')

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
        zip_code = form.zip_code.data
        radius = form.radius.data

        try:
            resp = requests.get(f"{RADIUS_BASE_URL}/{str(zip_code)}/{radius}/miles")

            res = resp.json()['zip_codes']

            zips = []

            for zip in res:
                zips.append(zip['zip_code'])

            session['response_zip_codes'] = zips

        except KeyError:
            flash('API demo request limit has been reached. Please try again in an hour. Sorry for the inconvenience.', 'danger')
            return render_template('search.html', form=form, page='search')
        
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
        return redirect("/")

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
            g.user.city=form.city.data
            g.user.state=form.state.data
            g.user.zip_code=form.zip_code.data
            
            # Clear current user's instruments list before adding form data
            g.user.instruments = []

            # Add form data to add instruments to current user's list
            for instrument in form.instruments.data:

                inst = Instrument.query.filter_by(name = instrument).first()
                User_Instrument.add_instrument_to_user(user_id=user.id, instrument_id=inst.id)
                db.session.add(inst)

            # Clear current user's genres list before adding form data
            g.user.genres = []

            # Add form data to add instruments to current user's list
            for genre in form.genres.data:
    
                gen = Genre.query.filter_by(name = genre).first()
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


@app.route('/users/update-password', methods=['GET','POST'])
def update_password():
    """Update current user's password."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")


    form = PasswordUpdateForm()

    if form.validate_on_submit():
        
        authenticated = User.authenticate(g.user.username,form.old_password.data)

        if authenticated and form.new_password.data == form.confirm_password.data:
            password = form.new_password.data
            g.user.password = bcrypt.generate_password_hash(password).decode('UTF-8')
            db.session.commit()

            flash('Successfully updated password.', 'success')
            return redirect(f"/users/{g.user.id}")

        flash('Passwords did not match.', 'danger')
        return redirect(f"/users/{g.user.id}")


    else:
        return render_template('edit-password.html',form=form, user=g.user)


@app.route('/messages/<int:user_id>', methods=['GET','POST'])
def send_message(user_id):
    """Send new message to a user"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/users/{g.user.id}")

    recipient = User.query.get_or_404(user_id)

    form = MessageForm()
    
    if form.validate_on_submit():
        
        recipient.add_notification('unread_message_count', recipient.new_messages())

        subject = form.subject.data
        body = form.body.data
        msg = Message(sender_id=g.user.id, recipient_id = user_id, subject=subject, body=body)

        db.session.add(msg)
        db.session.commit()

        flash("Message sent.", "success")
        return redirect(f'/users/{user_id}')

    else: 
        return render_template('send-message.html', sender=g.user, page='messages', recipient=recipient, form=form)

@app.route('/messages/<int:message_id>/delete', methods=['GET'])
def destroy_message(message_id):
    "Delete message from database"
   
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/users/{g.user.id}")

    Message.query.filter(Message.id==message_id).delete()
    db.session.commit()

    flash("Message deleted.", "success")
    return redirect('/messages')

@app.route('/messages')
def messages():
    if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/users/{g.user.id}")

    g.user.last_message_read_time = datetime.utcnow()
    g.user.add_notification('unread_message_count', 0)
    db.session.commit()

    page = request.args.get('page', 1, type=int)
    messages = g.user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url, page='messages')


@app.route('/notifications')
def notifications():
    """Update notifications using an AJAX call"""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    since = request.args.get('since', 0.0, type=float)

    notifications = g.user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])


#Follow Routes
@app.route('/following/<int:user_id>')
def show_follows(user_id):
    """Query and display all follows for a user."""

    user = User.query.get_or_404(user_id)
    users = user.following

    return render_template('following.html', title='Following', user=user,users=users)


@app.route('/follow/<int:user_id>', methods=['GET','POST'])
def follow_user(user_id):
    """Follow a user"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/users/{g.user.id}")

    if not g.user.is_following(user_id):
        
        follow = Follows(user_being_followed_id=user_id, user_following_id = g.user.id)
        db.session.add(follow)
        db.session.commit()
        return redirect(f"/users/{user_id}")
    return redirect(f"/users/{user_id}")


@app.route('/unfollow/<int:user_id>', methods=['GET','POST'])
def unfollow_user(user_id):
    """Unfollow a user"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/users/{g.user.id}")
    
    follow = Follows.query.filter(Follows.user_being_followed_id == user_id, Follows.user_following_id == g.user.id).one()
    db.session.delete(follow)
    db.session.commit()
    return redirect(f"/users/{user_id}")


@app.route('/followers/<int:user_id>')
def show_follower(user_id):
    """Query and display all followers for a user."""

    user = User.query.get_or_404(user_id)
    users = user.followers

    return render_template('followers.html', user=user,users=users)


@app.errorhandler(413)
def request_entity_too_large(error):
    """What happens if a file is too large."""

    if not g.user:
        return render_template('home-anon.html')

    user = g.user
    curr_user = g.user
    db.session.rollback()
    flash('The photo upload was too large. Please limit file uploads to <16MB.' + str(error), 'danger')
    return render_template('profile.html',413, user=user,curr_user=curr_user, page='profile')
    


@app.errorhandler(404)
def page_not_found(error):
    """What happens if a page not found."""
    
    return render_template('404.html',error=error),404

