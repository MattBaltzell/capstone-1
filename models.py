from datetime import datetime
from flask import g
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import json
from time import time

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
        db.String(),
        nullable=True,
        default="/static/uploads/default-pic.png",
    )

    header_image = db.Column(
        db.String(),
        nullable=True,
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

    messages_sent = db.relationship(
        'Message',
        foreign_keys='Message.sender_id',
        backref='author',
        lazy='dynamic'        
    )

    messages_received = db.relationship(
        'Message',
        foreign_keys='Message.recipient_id',
        backref='recipient',
        lazy='dynamic'        
    )

    last_message_read_time = db.Column(db.DateTime)

    notifications = db.relationship(
        'Notification', 
        backref='user',
        lazy='dynamic')

    
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

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n
    

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



class Genre(db.Model):
    """Genres."""

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
    """Which Users play which Genres?"""

    __tablename__ = 'users_genres'

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
    """Instruments."""

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
    """Which Users play which Instruments?"""

    __tablename__ = 'users_instruments'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
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

class Message(db.Model):
    """Messages"""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade")
    )

    recipient_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade")
    )

    subject = db.Column(
        db.Text,
        nullable=False,
    )

    body = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime, 
        index=True, 
        default=datetime.utcnow
    )


class Notification(db.Model):
    """Notifications."""

    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))


def connect_db(app):
    """Connect this database to provided Flask app"""

    db.app = app
    db.init_app(app)