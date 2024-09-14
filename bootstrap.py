import os
import json
import time

from app import app, db, DB_FILE
from models import *

# This file is used to bootstrap the database with initial data.
# It creates a user and adds the clubs from the clubs.json file to the database.
# It is only run once when the database is first created.

def create_user():
    user_josh = User(username="josh", email="josh@seas.upenn.edu", first_name="Josh", last_name="Allen",
                     school="SEAS", major="CIS", grad_year=2023)
    user_josh.set_password("password")
    db.session.add(user_josh)

# Iterates through the clubs.json file and adds each club to the database as an object.
# Tags are added seperately by adding them to the club's tags list after the club is created.
def load_data():
    t0 = time.time()
    with open("clubs.json", 'r') as file:
        clubs_data = json.load(file)
    for club_data in clubs_data:
        club = Club(code=club_data['code'], name=club_data['name'], description=club_data['description'])
        db.session.add(club)
        for tag_data in club_data['tags']:
            tag = Tag.query.filter_by(name=tag_data).first()
            if not tag:
                tag = Tag(name=tag_data)
                db.session.add(tag)
            club.tags.append(tag)
    db.session.commit()
    t1 = time.time()
    print(t1-t0)



# No need to modify the below code.
if __name__ == "__main__":
    # Delete any existing database before bootstrapping a new one.
    LOCAL_DB_FILE = "instance/" + DB_FILE
    if os.path.exists(LOCAL_DB_FILE):
        os.remove(LOCAL_DB_FILE)

    with app.app_context():
        db.create_all()
        create_user()
        load_data()