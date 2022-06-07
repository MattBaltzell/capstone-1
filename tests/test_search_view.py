"""Search View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py
import os
from unittest import TestCase
from models import db, connect_db, User, Instrument, Genre
from multiselect_options import INSTRUMENT_CHOICES, GENRE_CHOICES


os.environ['DATABASE_URL'] = "postgresql:///hook-find-musicians-test"
from app import app, CURR_USER_KEY

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


class SearchViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
    

        self.client = app.test_client()

        self.testband1 = User.signup(username='testband1',
                                    email='testband1@test.com',
                                    password='testuser',
                                    city='Test',
                                    state='AL',
                                    zip_code='99999',
                                    is_band=True,
                                    profile_image=None,
                                    header_image=None)

        self.testuser1 = User.signup(username='testuser1',
                                    email='test1@test.com',
                                    password='testuser',
                                    city='Test',
                                    state='AL',
                                    zip_code='11111',
                                    is_band=False,
                                    profile_image=None,
                                    header_image=None)

        self.testuser2 = User.signup(username='testuser2',
                                    email='test2@test.com',
                                    password='testuser',
                                    city='Test',
                                    state='AL',
                                    zip_code='22222',
                                    is_band=False,
                                    profile_image=None,
                                    header_image=None)

        self.testuser3 = User.signup(username='testuser3',
                                    email='test3@test.com',
                                    password='testuser',
                                    city='Test',
                                    state='AL',
                                    zip_code='33333',
                                    is_band=False,
                                    profile_image=None,
                                    header_image=None)

        db.session.commit()


    def test_render_search_form(self):
        """Does the search form render?"""

        with self.client as c:
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.get("/search")          
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="text-5xl leading-tight font-light lg:mt-6 lg:text-6xl">Find Musicians!</h1>',html )
            self.assertIn('<label for="is_band-0">Musicians</label>',html )
            self.assertIn('<label class="text-xl" for="instruments-search">Instrument Played</label>',html )
            self.assertIn('<label class="text-xl" for="genres-search">Genre Played</label>',html )
            self.assertIn('<input class="radius_slider" id="radius" max="100" min="0" name="radius" step="10" type="range" value="10"',html )
            

    def test_search_results(self):
        """Does the search form render?"""

        with self.client as c:
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

                #Simulating the form submission
                sess["searching_for_band"] = 'False'
                sess["searching_instrument"] = 'acoustic guitar'
                sess["searching_genre"] = 'rock'
                sess['response_zip_codes'] = ['11111','22222','33333','99999']

            band1 = User.query.filter(User.username == 'testband1').first()
            user1 = User.query.filter(User.username == 'testuser1').first()
            user2 = User.query.filter(User.username == 'testuser2').first()
            user3 = User.query.filter(User.username == 'testuser3').first()

            acoustic = Genre.query.filter(Genre.name == 'acoustic').first()
            alt_metal = Genre.query.filter(Genre.name == 'alt metal').first()
            blues = Genre.query.filter(Genre.name == 'blues').first()
            country = Genre.query.filter(Genre.name == 'country').first()
            dance = Genre.query.filter(Genre.name == 'dance').first()
            jazz = Genre.query.filter(Genre.name == 'jazz').first()
            metal = Genre.query.filter(Genre.name == 'metal').first()
            rock = Genre.query.filter(Genre.name == 'rock').first()
            
            acoustic_guitar = Instrument.query.filter(Instrument.name == 'acoustic guitar').first()
            drums = Instrument.query.filter(Instrument.name == 'drums').first()
            lead_guitar = Instrument.query.filter(Instrument.name == 'lead guitar').first()


            band1.instruments = [acoustic_guitar, lead_guitar]
            band1.genres = [rock,dance]
            user1.instruments = [acoustic_guitar]
            user1.genres = [rock,country,blues]
            user2.instruments = [lead_guitar]
            user2.genres = [jazz,acoustic]
            user3.instruments = [acoustic_guitar,lead_guitar,drums]
            user3.genres = [rock,metal,alt_metal]
            db.session.commit()

            resp = c.get("/results")          
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Search Results',html )
            self.assertNotIn('Testband1',html )
            self.assertIn('Testuser1',html )
            self.assertNotIn('Testuser2',html )
            self.assertIn('Testuser3',html )


            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

                #Simulating the form submission
                sess["searching_for_band"] = 'True'
                sess["searching_instrument"] = 'acoustic guitar'
                sess["searching_genre"] = 'rock'
                sess['response_zip_codes'] = ['11111','22222','33333','99999']

            resp = c.get("/results")          
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Search Results',html )
            self.assertIn('Testband1',html )
            self.assertNotIn('Testuser1',html )
            self.assertNotIn('Testuser2',html )
            self.assertNotIn('Testuser3',html )





            