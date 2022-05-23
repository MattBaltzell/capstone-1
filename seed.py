from csv import DictReader
from app import db
from models import User, Instrument, User_Instrument, User_Genre, Genre, Follows


# txt files for populating genres and instruments into fake user accounts
GENRE_CHOICES = "generator/genres.txt"
INSTRUMENT_CHOICES = "generator/instruments.txt"

# def create_multiform_choices(choices_file):
#     """Function for creating multiform choices from a list in a txt file"""
#     file = choices_file
#     result = []
#     with open(file, "rb") as choices:
#         for choice in choices.readlines():
            
#             try:
#                 result.append((str(choice), str(choice.title())))
#             except:pass
#     return result

def create_list_from_txt(lists_file):
    """Function for creating multiform lists from a list in a txt file"""
    file = lists_file
    result = []
    with open(file, "r") as list:
        for item in list.readlines():
            try:
                result.append(item.strip())
            except:pass
    return result




db.drop_all()
db.create_all()

with open('generator/users.csv') as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

with open('generator/follows.csv') as follows:
    db.session.bulk_insert_mappings(Follows, DictReader(follows))



#CREATE INSTRUMENTS AND GENRES
instruments_list = create_list_from_txt(INSTRUMENT_CHOICES)
genres_list = create_list_from_txt(GENRE_CHOICES)

for instrument in instruments_list:
    inst = Instrument(name=instrument)

    db.session.add(inst)

for genre in genres_list:
    g = Genre(name=genre)

    db.session.add(g)

    
db.session.commit()

with open('generator/users_instruments.csv') as users_instruments:
    db.session.bulk_insert_mappings(User_Instrument, DictReader(users_instruments))

with open('generator/users_genres.csv') as users_genres:
    db.session.bulk_insert_mappings(User_Genre, DictReader(users_genres))

db.session.commit()
