"""User model tests."""

#    python -m unittest test_user_model.py

import os
from unittest import TestCase
from models import db, User, Follows, Instrument, User_Instrument, Genre, User_Genre

os.environ['DATABASE_URL'] = "postgresql:///hook-find-musicians-test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test User Model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Follows.query.delete()
        Instrument.query.delete()
        Genre.query.delete()

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
            profile_image=User.profile_image.default.arg,
            header_image=User.header_image.default.arg,
            city='TestCity',
            state='TS',
            zip_code='12345'
        )

        db.session.add(u)
        db.session.commit()
        
        # User should have no followers, following, genres, or instruments
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)
        self.assertEqual(len(u.genres), 0)
        self.assertEqual(len(u.instruments), 0)

        # User __repr__ method should work correctly
        self.assertEqual(u.__repr__(),f'<User #{u.id}: testuser, test@test.com>' )
        self.assertEqual(u.is_band, False)
        self.assertEqual(u.profile_image, "/static/uploads/default-pic.png")
        self.assertEqual(u.header_image, "/static/uploads/default-header-pic.jpg")
        self.assertEqual(u.city, "TestCity")
        self.assertEqual(u.state, "TS")
        self.assertEqual(u.zip_code, "12345")
   
    def test_signup_method(self):
        """Check if signup method returns user whengiven valid credentials"""

        u = User.signup(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD",
            city="Test City",
            state="TS",
            zip_code='36832',
            is_band=False,
            header_image=User.header_image.default.arg,
            profile_image=User.profile_image.default.arg
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(u.username, 'testuser')
        self.assertEqual(u.email, 'test@test.com')
        self.assertNotEqual(u.password, 'HASHED_PASSWORD')
        self.assertFalse(u.is_band)
        self.assertEqual(u.profile_image, '/static/uploads/default-pic.png')
        self.assertEqual(u.header_image, '/static/uploads/default-header-pic.jpg')
        self.assertIsNotNone(u.city)
        self.assertEqual(u.city, "Test City")
        self.assertIsNotNone(u.state)
        self.assertEqual(u.state, "TS")
        self.assertEqual(u.zip_code, '36832')
      


    def test_authenticate_method(self):
        """Check if authenticate method returns user if valid username and pword are given. Fails to return user if invalid username or pword."""
         
        u = User.signup(
            username='testuser',
            email='test@test.com',
            password='HASHED_PASSWORD',
            city='Test City',
            state='ST',
            zip_code='36832',
            is_band=True,
            profile_image=User.profile_image.default.arg,
            header_image=User.header_image.default.arg
        )

        db.session.add(u)
        db.session.commit()

        auth_user = User.authenticate('testuser','HASHED_PASSWORD')
       
        self.assertEqual(auth_user, u)
        self.assertEqual(auth_user.username, 'testuser')
        self.assertEqual(auth_user.email, 'test@test.com')
        self.assertNotEqual(auth_user.password, 'HASHED_PASSWORD')
        self.assertTrue(auth_user.is_band)
        self.assertEqual(auth_user.profile_image, '/static/uploads/default-pic.png')
        self.assertEqual(auth_user.header_image, '/static/uploads/default-header-pic.jpg')
        self.assertIsNotNone(auth_user.city)
        self.assertIsNotNone(auth_user.state)
        self.assertEqual(auth_user.zip_code, '36832')
        self.assertEqual(auth_user.instruments, [])
        self.assertEqual(auth_user.genres, [])
        
        auth_fail_user1 = User.authenticate('testuser','WRONG_PASSWORD')
        auth_fail_user2 = User.authenticate('WRONG_USERNAME','HASHED_PASSWORD')
        self.assertEqual(auth_fail_user1, False)
        self.assertEqual(auth_fail_user2, False)


    def test_user_relationship(self):
        """Test ."""
         
        u = User.signup(
            username='testuser',
            email='test@test.com',
            password='HASHED_PASSWORD',
            city='Test City',
            state='ST',
            zip_code='36832',
            is_band=True,
            profile_image=User.profile_image.default.arg,
            header_image=User.header_image.default.arg
        )

        i = Instrument(name='Test Instrument')
        g = Genre(name='Test Genre')
        
        db.session.add(u)
        db.session.add(i)
        db.session.add(g)
        db.session.commit()

        u_i = User_Instrument(user_id=u.id, instrument_id=i.id)
        u_g = User_Genre(user_id=u.id, genre_id=g.id)
        db.session.add(u_i)
        db.session.add(u_g)
        db.session.commit()

        self.assertIsNotNone(u.instruments)
        self.assertIn(i, u.instruments)
        self.assertEqual(u.instruments[0].name,'Test Instrument')
        self.assertIsNotNone(i.users)
        self.assertEqual(i.users[0].username,'testuser')
        
        self.assertIsNotNone(u.genres)
        self.assertIn(g, u.genres)
        self.assertEqual(u.genres[0].name,'Test Genre')
        self.assertIsNotNone(g.users)
        self.assertEqual(g.users[0].username,'testuser')
        