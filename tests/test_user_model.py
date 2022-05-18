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
            image_url=User.image_url.default.arg,
            header_image_url=User.header_image_url.default.arg,
            city='TestCity',
            state='TestState',
            zip_code='12345'
        )

        db.session.add(u)
        db.session.commit()
        
        # User should have no posts, followers, following, likes, genres, instruments or songs
        self.assertEqual(len(u.posts), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)
        self.assertEqual(len(u.likes), 0)
        self.assertEqual(len(u.genres), 0)
        self.assertEqual(len(u.instruments), 0)
        self.assertEqual(len(u.songs), 0)
        self.assertNotEqual(len(u.songs), 10)
        # User __repr__ method should work correctly
        self.assertEqual(u.__repr__(),f'<User #{u.id}: testuser, test@test.com>' )
        self.assertEqual(u.is_band, False)
        self.assertEqual(u.image_url, "/static/images/default-pic.png")
        self.assertEqual(u.header_image_url, "/static/images/default-header-pic.jpg")
        self.assertEqual(u.city, "TestCity")
        self.assertEqual(u.state, "TestState")
        self.assertEqual(u.zip_code, "12345")
   
    def test_signup_method(self):
        """Check if signup method returns user whengiven valid credentials"""

        u = User.signup(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD",
            zip_code='36832',
            is_band=False,
            image_url=User.image_url.default.arg
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(u.username, 'testuser')
        self.assertEqual(u.email, 'test@test.com')
        self.assertNotEqual(u.password, 'HASHED_PASSWORD')
        self.assertFalse(u.is_band)
        self.assertEqual(u.image_url, '/static/images/default-pic.png')
        self.assertEqual(u.header_image_url, '/static/images/default-header-pic.jpg')
        self.assertIsNone(u.city)
        self.assertIsNone(u.state)
        self.assertEqual(u.zip_code, '36832')
      


    def test_authenticate_method(self):
        """Check if authenticate method returns user if valid username and pword are given. Fails to return user if invalid username or pword."""
         
        u = User.signup(
            username='testuser',
            email='test@test.com',
            password='HASHED_PASSWORD',
            zip_code='36832',
            is_band=True,
            image_url=User.image_url.default.arg
        )

        db.session.add(u)
        db.session.commit()

        auth_user = User.authenticate('testuser','HASHED_PASSWORD')
       
        self.assertEqual(auth_user, u)
        self.assertEqual(auth_user.username, 'testuser')
        self.assertEqual(auth_user.email, 'test@test.com')
        self.assertNotEqual(auth_user.password, 'HASHED_PASSWORD')
        self.assertTrue(auth_user.is_band)
        self.assertEqual(auth_user.image_url, '/static/images/default-pic.png')
        self.assertEqual(auth_user.header_image_url, '/static/images/default-header-pic.jpg')
        self.assertIsNone(auth_user.city)
        self.assertIsNone(auth_user.state)
        self.assertEqual(auth_user.zip_code, '36832')
        
        auth_fail_user1 = User.authenticate('testuser','WRONG_PASSWORD')
        auth_fail_user2 = User.authenticate('WRONG_USERNAME','HASHED_PASSWORD')
        self.assertEqual(auth_fail_user1, False)
        self.assertEqual(auth_fail_user2, False)





