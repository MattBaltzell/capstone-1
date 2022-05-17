"""User model tests."""

#    python -m unittest test_user_model.py

import os
from unittest import TestCase
from models import db, User, Likes, Follows, Instrument, Genre, Post

os.environ['DATABASE_URL'] = "postgresql:///hook-find-musicians-test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test User Model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Likes.query.delete()
        Follows.query.delete()
        Instrument.query.delete()
        Genre.query.delete()
        Post.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any bad transactions"""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            is_band=False,
            
        )

        db.session.add(u)
        db.session.commit()
        
        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        # User __repr__ method should work correctly
        self.assertEqual(u.__repr__(),f'<User #{u.id}: testuser, test@test.com>' )

    def test_following_methods(self):
        """Check if 'is_following' and 'is_followed_by' methods successfully detect when users are and are not being followed"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        f = Follows(
            user_being_followed_id=u2.id, 
            user_following_id=u1.id
            )

        db.session.add(f)
        db.session.commit()

        self.assertEqual(u1.is_following(u2), True)
        self.assertEqual(u2.is_followed_by(u1), True)
        self.assertNotEqual(u2.is_following(u1), True)
        self.assertNotEqual(u1.is_followed_by(u2), True)


    def test_signup_method(self):
        """Check if signup method returns user whengiven valid credentials"""

        u3 = User.signup(
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD",
            image_url=User.image_url.default.arg
        )

        db.session.add(u3)
        db.session.commit()

        self.assertEqual(u3.username, 'testuser3')
        self.assertEqual(u3.image_url, '/static/images/default-pic.png')
        self.assertEqual(u3.header_image_url, '/static/images/warbler-hero.jpg')


    def test_authenticate_method(self):
        """Check if authenticate method returns user if valid username and pword are given. Fails to return user if invalid username or pword."""
         
        u4 = User.signup(
            email="test4@test.com",
            username="testuser4",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png"
        )

        db.session.add(u4)
        db.session.commit()

        auth_user = User.authenticate("testuser4","HASHED_PASSWORD")
       
        self.assertEqual(auth_user, u4)
        self.assertEqual(auth_user.username, "testuser4")
        self.assertEqual(auth_user.email, "test4@test.com")
        self.assertEqual(auth_user.image_url, "/static/images/default-pic.png")
        
        auth_fail_user1 = User.authenticate("testuser4","WRONG_PASSWORD")
        auth_fail_user2 = User.authenticate("WRONG_USERNAME","HASHED_PASSWORD")
        self.assertEqual(auth_fail_user1, False)
        self.assertEqual(auth_fail_user2, False)
        



