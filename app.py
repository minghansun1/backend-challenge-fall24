from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

DB_FILE = "clubreview.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
db = SQLAlchemy(app)

SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'
print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY

from models import *


# This API allows users to interact with the Penn Club Review database. The API has the following endpoints:
# GET /api/clubs: Returns all clubs in the database as a JSON list.
# GET /api/clubs/<string:name>: Returns all clubs that contain the given string in its name as a JSON list.
# GET /api/users/<int:user_id>: Returns information of a user with the given userid as a JSON dictionary.
# GET /api/tags/clubcount: Returns all tag names and the number of clubs associated with each tag as a list of dictionaries.
# PUT /api/users/<int:user_id>/clubs/<string:code>: Lets a student favorite a club.
# PUT /api/clubs/<string:code>: Modifies a club.
# POST /api/clubs: Creates a new club with a code, name, description, and tags.

# When passing data into an API, the data should be in JSON format.
# The exception is for passing unique identifiers,such as user ids and club codes, which should be passed as
# http parameters.


@app.route("/")
def main():
    return "Welcome to Penn Club Review!"


@app.route("/api")
def api():
    return jsonify({"message": "Welcome to the Penn Club Review API!"})


# Returns all clubs in the database as a JSON object. If there are no clubs, returns an empty list.
@app.route("/api/clubs", methods=["GET"])
def get_all_clubs():
    clubs = Club.query.all()
    return jsonify([club.to_dict() for club in clubs]), 200


# Returns all clubs that contain the given string in its name as a JSON object.

# If the name is empty or None, returns a 400 error.
# If there are no clubs in the database, returns an empty list.
@app.route("/api/clubs/<string:name>", methods=["GET"])
def search_clubs(name: str):
    if name == "" or name is None:
        return jsonify({"message": "No name entered"}), 400

    name = str.lower(name)
    clubs_to_return = []
    for club in Club.query.all():
        if name in str.lower(club.name):
            clubs_to_return.append(club.to_dict())

    return jsonify(clubs_to_return), 200


# Returns all information of a user (except password) with the given userid as a JSON object.

# If no user id is given, returns a 400 error.
# If the user is not found, returns a 404 error.
@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    if user_id is None:
        return jsonify({"message": "No user id entered"}), 400

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    else:

        return jsonify(user.to_dict()), 200


# Returns all tag names and the number of clubs associated with each tag as a list of dictionaries.
# If there are no tags in the database, returns an empty list.
@app.route("/api/tags/clubcount", methods=["GET"])
def get_clubcount_for_tags():
    tags = Tag.query.all()
    tags_data_to_return = []
    for tag in tags:
        name = tag.to_dict()["name"]
        num_clubs = len(tag.to_dict()["clubs"])
        tags_data_to_return.append({"tag_name": name, "num_clubs": num_clubs})

    return jsonify(tags_data_to_return), 200


# Lets a student favorite a club. This increments the number of favorites a club has
# and adds the club to the user's list of favorite clubs.

# If the user or club is not found, returns a 404 error.
# If the club is already in the user's favorites, doesn't change the database and immediately returns a 200 error.
@app.route("/api/users/<int:user_id>/clubs/<string:code>", methods=["Put"])
def add_favorite_club(user_id: int, code: str):
    user = User.query.filter_by(id=user_id).first()
    club = Club.query.filter_by(code=code).first()
    if user is None or club is None:
        return jsonify({"message": "User or Club not found"}), 404
    if club in user.fav_clubs:
        return jsonify({"message": "Club already in favorites"}), 200

    user.fav_clubs.append(club)
    club.users.append(user)
    club.favorites += 1
    db.session.commit()

    return jsonify({"message": "Club added to favorites"}), 200


# Modifies a club. The club's name, description, and tags can be modified.
# The code cannot be modified since it's a unique identifier.

# If the request is not JSON, returns a 400 error.
# If the club is not found, returns a 404 error.
@app.route("/api/clubs/<string:code>", methods=["Put"])
def modify_club(code: str):
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400
    club = Club.query.filter_by(code=code).first()
    if club is None:
        return jsonify({"message": "Club not found"}), 404

    data = request.get_json()
    if "name" in data:
        club.name = data["name"]
    if "description" in data:
        club.description = data["description"]
    if "tags" in data:
        club.tags = []
        for curr_tag in data['tags']:
            tag = Tag.query.filter_by(name=curr_tag).first()
            if not tag:
                tag = Tag(name=tag)
                db.session.add(tag)
            club.tags.append(tag)
    db.session.commit()

    return jsonify({"message": "Club updated"}), 200


# Creates a new club with a code, name, description, and tags.

# If the request is not JSON, returns a 400 error.
# If the request does not contain code, name, description, and tags, returns a 400 error.
# If the club code already exists, returns a 400 error.
@app.route("/api/clubs", methods=["Post"])
def create_club():
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400
    data = request.get_json()
    if "code" not in data or "name" not in data or "description" not in data or "tags" not in data:
        return jsonify({"message": "Request must contain code, name, description, and tags"}), 400
    if (Club.query.filter_by(code=data['code']).first() is not None):
        return jsonify({"message": "Club code is taken"}), 400

    club = Club(code=data['code'], name=data['name'], description=data['description'])
    db.session.add(club)
    for tag_data in data['tags']:
        tag = Tag.query.filter_by(name=tag_data).first()
        if not tag:
            tag = Tag(name=tag_data)
            db.session.add(tag)
        club.tags.append(tag)
    db.session.commit()

    return jsonify({"message": "Club added"}), 200


if __name__ == "__main__":
    app.run()
