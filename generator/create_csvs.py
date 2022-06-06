
"""Generate CSVs of random data for Warbler.
Students won't need to run this for the exercise; they will just use the CSV
files that this generates. You should only need to run this if you wanted to
tweak the CSV formats or generate fewer/more rows.
"""

import csv
from random import choice, choices, randint, sample
from itertools import permutations
import requests
from faker import Faker
from helpers import get_random_datetime

MAX_BIO_LENGTH = 400

USERS_CSV_HEADERS = ['email', 'username', 'profile_image', 'password', 'bio', 'header_image', 'city', 'state', 'zip_code', 'instruments','genres']

FOLLOWS_CSV_HEADERS = ['user_being_followed_id', 'user_following_id']

USERS_INSTRUMENTS_CSV_HEADERS = ['id', 'user_id', 'instrument_id']

NUM_USERS = 50
NUM_FOLLWERS = 200

fake = Faker()

# Generate random profile image URLs to use for users

image_urls = [
    f"https://randomuser.me/api/portraits/{kind}/{i}.jpg"
    for kind, count in [("lego", 10), ("men", 100), ("women", 100)]
    for i in range(count)
]

# Generate random header image URLs to use for users

header_image_urls = [
    requests.get(f"http://www.splashbase.co/api/v1/images/{i}").json()['url']
    for i in range(1, 46)
]

sample_zip_codes = [36830,36832,36022, 36054, 36066, 35242, 36117, 36695, 35758]


with open('users.csv', 'w') as users_csv:
    users_writer = csv.DictWriter(users_csv, fieldnames=USERS_CSV_HEADERS)
    users_writer.writeheader()

    for i in range(NUM_USERS):
        users_writer.writerow(dict(
            email=fake.email(),
            username=fake.user_name(),
            profile_image=choice(image_urls),
            password='$2b$12$Q1PUFjhN/AWRQ21LbGYvjeLpZZB6lfZ1BPwifHALGO6oIbyC3CmJe',
            bio=fake.paragraph()[:MAX_BIO_LENGTH],
            header_image=choice(header_image_urls),
            city=fake.city(),
            state='AL',
            zip_code=choice(sample_zip_codes)))


# Generate follows.csv from random pairings of users

with open('follows.csv', 'w') as follows_csv:
    all_pairs = list(permutations(range(1, NUM_USERS + 1), 2))

    users_writer = csv.DictWriter(follows_csv, fieldnames=FOLLOWS_CSV_HEADERS)
    users_writer.writeheader()

    for followed_user, follower in sample(all_pairs, NUM_FOLLWERS):
        users_writer.writerow(dict(user_being_followed_id=followed_user, user_following_id=follower))



