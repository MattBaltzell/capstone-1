"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py
import os, io
from unittest import TestCase
from models import db, connect_db, Message, User, Instrument, Genre, Notification
from multiselect_options import INSTRUMENT_CHOICES, GENRE_CHOICES


os.environ['DATABASE_URL'] = "postgresql:///hook-find-musicians-test"
from app import app, CURR_USER_KEY

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
    

        self.client = app.test_client()

        self.testuser1 = User.signup(username='testuser1',
                                    email='test1@test.com',
                                    password='testuser',
                                    city='Test',
                                    state='AL',
                                    zip_code='36830',
                                    is_band=False,
                                    profile_image=None,
                                    header_image=None)

        self.testuser2 = User.signup(username='testuser2',
                                    email='test2@test.com',
                                    password='testuser',
                                    city='Test',
                                    state='AL',
                                    zip_code='36830',
                                    is_band=False,
                                    profile_image=None,
                                    header_image=None)

        self.testuser3 = User.signup(username='testuser3',
                                    email='test3@test.com',
                                    password='testuser',
                                    city='Test',
                                    state='AL',
                                    zip_code='36830',
                                    is_band=False,
                                    profile_image=None,
                                    header_image=None)

        db.session.commit()


    def test_user_profile(self):
        """Do users show up in list?"""

        with self.client as c:
            
            user = User.query.first()

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.get(f"users/{user.id}")          
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="text-3xl md:text-4xl font-medium md:mt-16">Testuser1</h1>',html )
            self.assertIn('<p class="text-md"><span><i class="fa-solid fa-location-dot text-emerald-400 text-md w-[15px]"></i></span> Test, AL 36830</p>',html )
            self.assertIn('/static/uploads/default-pic.png',html )
            self.assertIn('MUSICIAN',html )
            
            
    def test_edit_user_profile(self):
        """Does the form render and redirect to profile on submit?"""

        with self.client as c:
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            #CREATE INSTRUMENTS AND GENRES
            for instrument in INSTRUMENT_CHOICES:
                inst = Instrument(name=instrument)
                db.session.add(inst)
                
            for genre in GENRE_CHOICES:
                g = Genre(name=genre)
                db.session.add(g)

            db.session.commit()

            resp = c.get("/users/edit")          
            html = resp.get_data(as_text=True)

            #Does the edit form page render?
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="text-5xl leading-tight font-light mb-2">Edit Profile</h1>',html )
            self.assertIn('testuser1',html )
            self.assertIn('Test',html )
            self.assertIn('36830',html )
            self.assertIn('To confirm changes, enter your password:',html )

            #Does updated form submit and redirect to profile page with updated info?
            form_data = {"username":"testuser1 edited","email":"test1edited@test.com", "city":"Test Edited", "state":"ED", "zip_code":"11111","bio":"Test bio."}
            form_data['header_image'] = (io.BytesIO(b"abcdef"), 'test_header_image.jpg')
            form_data['profile_image'] = (io.BytesIO(b"abcdef"), 'test_profile_image.jpg')
            form_data['instruments'] = ['acoustic guitar']
            form_data['genres'] = ['rock']
            form_data['password'] = "testuser"

            resp = c.post("/users/edit", data=form_data, follow_redirects=True,headers={"Content-Type":"multipart/form-data"})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('field_error',html )
            self.assertIn('FOLLOWERS',html )
            self.assertIn('FOLLOWING',html )
            self.assertIn('<h1 class="text-3xl md:text-4xl font-medium md:mt-16">Testuser1 Edited</h1>',html)
            self.assertIn('Acoustic Guitar',html )
            self.assertNotIn('Lead Guitar',html )
            self.assertIn('Rock',html )
            self.assertNotIn('Alt Metal',html )
            self.assertIn('test_profile_image.jpg alt=testuser1 edited',html )
            self.assertIn('<p class="">Test bio.</p>',html )



    def test_user_login(self):
        """Does the login form render and redirect to profile on submit?"""

        with self.client as c:
            
            resp = c.get("/login")          
            html = resp.get_data(as_text=True)

            #Does the login form page render?
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<img src="/static/img/hook-logo-grn.svg" class="box-border h-8 w-24 self-center" alt="hook">',html )
            self.assertIn('<h1 class="text-6xl font-light mb-2">Login</h1>',html )
            self.assertIn('<p class="text-lg ">Please sign in to continue.</p>',html )
            self.assertIn('<input class="rounded border-1 border-stone-400 placeholder:text-xs placeholder:font-extrabold placeholder:uppercase placeholder:text-stone-400" id="username" name="username" placeholder="Username" required type="text" value="">',html )
            self.assertIn('<input class="rounded border-1 border-stone-400 placeholder:text-xs placeholder:font-extrabold placeholder:uppercase placeholder:text-stone-400" id="password" minlength="6" name="password" placeholder="Password" type="password" value="">',html )
            
            #Does updated form submit and redirect to profile page with updated info?
            form_data = {"username":"testuser2","password":"testuser"}
            
            resp = c.post("/login", data=form_data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('field_error',html )
            self.assertIn('<h1 class="text-5xl leading-tight font-light lg:mt-6 lg:text-6xl">Find Musicians!</h1>',html )
            self.assertIn('<input class="rounded border-1 border-slate-400 placeholder:text-xs placeholder:font-extrabold placeholder:uppercase placeholder:text-slate-400 mb-3" id="zip_code" max="99999" min="0" name="zip_code" placeholder="Zip Code" required type="number" value="">',html )
            
    def test_user_registration(self):
        """Does the signup form render and redirect to profile on submit?"""

        with self.client as c:
            
            resp = c.get("/signup")          
            html = resp.get_data(as_text=True)

            #Does the signup form page render?
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<img src="/static/img/hook-logo-grn.svg" class="box-border h-8 w-24 self-center" alt="hook">',html )
            self.assertIn('<h1 class="text-5xl font-light text-center">Create Account</h1>',html )
            self.assertIn('<input class="rounded border-1 border-stone-400 placeholder:text-xs placeholder:font-extrabold placeholder:uppercase placeholder:text-stone-400" id="username" name="username" placeholder="Username" required type="text" value="">',html )
            self.assertIn('<input class="rounded border-1 border-stone-400 placeholder:text-xs placeholder:font-extrabold placeholder:uppercase placeholder:text-stone-400" id="password" minlength="6" name="password" placeholder="Password" type="password" value="">',html )
            self.assertIn('<label for="is_band">Is this a band page?</label>',html )
            
            #Does updated form submit and redirect to profile page with updated info?
            form_data = {"username":"testuser4","email":"test4@test.com","password":"testuser4","city":"Test City", "state":"AK","zip_code":36022,"is_band":"f"}
            
            resp = c.post("/signup", data=form_data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="text-3xl md:text-4xl font-medium md:mt-16">Testuser4</h1>',html )
            self.assertIn('<p class="text-md"><span><i class="fa-solid fa-location-dot text-emerald-400 text-md w-[15px]"></i></span> Test City, AK 36022</p>',html )
            self.assertIn('<img src=/static/uploads/default-pic.png alt=testuser4  class="w-48 h-48 rounded-full bg-white object-cover  border-[3px] md:border-[4px] border-white">',html )

