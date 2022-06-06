from csv import DictReader
from app import db
from multiselect_options import INSTRUMENT_CHOICES, GENRE_CHOICES
from models import User, Instrument, User_Instrument, User_Genre, Genre, Follows

db.create_all()

#CREATE INSTRUMENTS AND GENRES
for instrument in INSTRUMENT_CHOICES:
    inst = Instrument(name=instrument)
    db.session.add(inst)
   
for genre in GENRE_CHOICES:
    g = Genre(name=genre)
    db.session.add(g)
 

with open('generator/users.csv') as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

with open('generator/follows.csv') as follows:
    db.session.bulk_insert_mappings(Follows, DictReader(follows))


with open('generator/users_instruments.csv') as users_instruments:
    db.session.bulk_insert_mappings(User_Instrument, DictReader(users_instruments))

with open('generator/users_genres.csv') as users_genres:
    db.session.bulk_insert_mappings(User_Genre, DictReader(users_genres))

db.session.commit()
