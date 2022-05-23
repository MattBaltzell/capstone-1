from datetime import datetime
from flask import g
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class Follows(db.Model):
    """Connection of a follower <-> followed_user."""

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )


class Likes(db.Model):
    """Mapping user likes to posts."""

    __tablename__ = 'likes' 

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey('posts.id', ondelete='cascade')
    )

class Song(db.Model):
    """"""

    __tablename__ = 'songs' 

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    duration = db.Column(
        db.Integer,
        nullable=False,
    )

    song_url = db.Column(
        db.Text,
        nullable=False,
    )


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )
    
    password = db.Column(
        db.Text,
        nullable=False,
    )

    is_band = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    profile_image = db.Column(
        db.Text,
        default="/static/uploads/default-pic.png",
    )

    header_image = db.Column(
        db.Text,
        default="/static/uploads/default-header-pic.jpg"
    )

    bio = db.Column(
        db.Text,
    )

    city = db.Column(
        db.Text,
    )

    state = db.Column(
        db.Text,
    )

    zip_code = db.Column(
        db.String,
    )
    
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    posts = db.relationship('Post')

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id),
        overlaps="followers"
    )

    likes = db.relationship(
        'Post',
        secondary="likes"
    )

    genres = db.relationship(
        'Genre',
        secondary="users_genres",
        backref="users"
    )

    instruments = db.relationship(
        'Instrument',
        secondary="users_instruments",
        backref="users"
    )

    songs = db.relationship(
        'Song',
        secondary="users_songs",
        backref="users"
    )


    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is this user following `other_user`?"""

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1

    

    @classmethod
    def signup(cls, username, email, password, city, state, zip_code, is_band, profile_image, header_image):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            city=city,
            state=state,
            zip_code=zip_code,
            is_band=is_band,
            profile_image=profile_image or User.profile_image.default.arg,
            header_image=header_image or User.header_image.default.arg,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()
        
        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class User_Song(db.Model):
    """"""

    __tablename__ = 'users_songs'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
    )

    song_id = db.Column(
        db.Integer,
        db.ForeignKey('songs.id'),
        nullable=False,
    )


class Post(db.Model):
    """A user post that will display on feed."""

    __tablename__ = 'posts'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    post_text = db.Column(
        db.String(140),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )


    user = db.relationship('User')



class Genre(db.Model):
    """"""

    __tablename__ = 'genres'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

class User_Genre(db.Model):
    """"""

    __tablename__ = 'users_genres'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
    )

    genre_id = db.Column(
        db.Integer,
        db.ForeignKey('genres.id'),
        nullable=False,
    )

    @classmethod
    def add_genre_to_user(self,user_id,genre_id):
        """Add genre to user"""

        if user_id == g.user.id: 
            new_user_genre = User_Genre(user_id=user_id,genre_id=genre_id)
            db.session.add(new_user_genre)
            return new_user_genre
        else:
            return None


class Instrument(db.Model):
    """"""

    __tablename__ = 'instruments'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

class User_Instrument(db.Model):
    """"""

    __tablename__ = 'users_instruments'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
    )

    instrument_id = db.Column(
        db.Integer,
        db.ForeignKey('instruments.id'),
        nullable=False,
    )

    @classmethod
    def add_instrument_to_user(self,user_id,instrument_id):
        """Add instrument to user"""

        if user_id == g.user.id: 
            new_user_instrument = User_Instrument(user_id=user_id,instrument_id=instrument_id)
            db.session.add(new_user_instrument)
            return new_user_instrument
        else:
            return None


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)


