from flask import Flask, request, jsonify
from sqlalchemy import func
from sqlalchemy.orm import joinedload
import os
from db import db

DB_FILE = "clubreview.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
db.init_app(app)

SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret_key'
app.config['SECRET_KEY'] = SECRET_KEY

from models import *

'''
This API allows users to interact with the Penn Club Review database. The API has the following endpoints:
GET /api/clubs: Returns all clubs in the database as a JSON list.
GET /api/clubs/<string:name>: Returns all clubs that contain the given string in its name as a JSON list.
GET /api/users/<int:user_id>: Returns information of a user with the given userid as a JSON dictionary.
GET /api/tags: Returns all tag names and the number of clubs associated with each tag as a list of dictionaries.
GET /api/clubs/<string:code>/comments: Returns all comments for a club with the given code as a JSON list.
GET /api/users/<int:user_id>/comments: Returns all comments by a user with the given userid as a JSON list.
PUT /api/users/<int:user_id>/clubs/<string:code>/favorite: Lets a student favorite a club.
PUT /api/users/<int:user_id>/clubs/<string:code>/unfavorite: Lets a student unfavorite a club.
PUT /api/clubs/<string:code>: Modifies a club.
PUT /api/users/<int:user_id>/clubs/<string:code>/comment/<int:comment_id>: Edits a comment about a club with the given code.
POST /api/clubs: Creates a new club with a code, name, description, and tags.
POST /api/users/<int:user_id>/clubs/<string:code>/comments: Adds a comment to a club with the given code.
POST /api/users/<int:user_id>/clubs/<string:code>/comments/<int:comment_id>: Replies to a comment about a club with the given code.

When passing data into an API, the data should be in JSON format.
The exception is for passing unique identifiers, such as user ids and club codes, which should be passed as
http parameters.
'''


@app.route("/")
def main():
    return "Welcome to Penn Club Review!"


@app.route("/api")
def api():
    return jsonify({"message": "Welcome to the Penn Club Review API!"})


# Returns all clubs in the database as a JSON object. If there are no clubs, returns an empty list.
@app.route("/api/clubs", methods=["GET"])
def get_all_clubs():
    clubs = db.session.query(Club).all()
    return jsonify([club.to_dict() for club in clubs]), 200


# Returns all clubs that contain the given string in its name as a JSON object.
# If the name is empty or None, returns a 400 error.
# If there are no clubs in the database, returns an empty list.
@app.route("/api/clubs/<string:name>", methods=["GET"])
def search_clubs(name: str):
    if not name:
        return jsonify({"message": "No name entered"}), 400
    
    name_lower = f"%{name.lower()}%"
    clubs = db.session.query(Club).filter(func.lower(Club.name).like(name_lower)).all()
    return jsonify([club.to_dict() for club in clubs]), 200


# Returns all information of a user (except password hash and list of favorited clubs) with the given userid as a JSON object.
# If no user id is given, returns a 400 error.
# If the user is not found, returns a 404 error.
@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    if user_id is None:
        return jsonify({"message": "No user id entered"}), 400

    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    else:
        return jsonify(user.to_public_dict()), 200


# Returns all tag names and the number of clubs associated with each tag as a list of dictionaries.
# If there are no tags in the database, returns an empty list.
@app.route("/api/tags", methods=["GET"])
def get_tags():
    tag_club_counts = db.session.query(
        Tag.name, func.count(Club.id).label('num_clubs')
    ).outerjoin(Tag.clubs).group_by(Tag.id).all()

    tags_data_to_return = [{"tag_name": tag_name, "num_clubs": num_clubs} for tag_name, num_clubs in tag_club_counts]

    return jsonify(tags_data_to_return), 200


# Returns all comments for a club with the given code as a JSON object.
# If the club is not found, returns a 404 error.
@app.route("/api/clubs/<string:code>/comments", methods=["GET"])
def get_club_comments(code: str):
    club = db.session.query(Club).filter_by(code=code).first()
    if not club:
        return jsonify({"message": "Club not found"}), 404
    
    return jsonify([comment.to_dict() for comment in club.comments]), 200


# Returns all comments for a user with the given code as a JSON object.
# If the user is not found, returns a 404 error.
@app.route("/api/users/<int:user_id>/comments", methods=["GET"])
def get_user_comments(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify([comment.to_dict() for comment in user.comments]), 200


# Lets a student favorite a club. This increments the number of favorites a club has
# and adds the club to the user's list of favorite clubs.
# If the user or club is not found, returns a 404 error.
# If the club is already in the user's favorites, doesn't change the database and immediately returns a 200 error.
@app.route("/api/users/<int:user_id>/clubs/<string:code>/favorite", methods=["PUT"])
def add_favorite_club(user_id: int, code: str):
    user = User.query.get(user_id)
    club = Club.query.filter_by(code=code).first()

    if user is None or club is None:
        return jsonify({"message": "User or Club not found"}), 404
    if club in user.fav_clubs:
        return jsonify({"message": "Club already in favorites"}), 200

    user.fav_clubs.append(club)
    club.favorites += 1
    db.session.commit()
    return jsonify({"message": "Club added to favorites"}), 200


# Lets a student unfavorite a club. This decrements the number of favorites a club has
# and adds the club to the user's list of favorite clubs.
# If the user or club is not found, returns a 404 error.
# If the club is already in the user's favorites, doesn't change the database and immediately returns a 200 error.
@app.route("/api/users/<int:user_id>/clubs/<string:code>/unfavorite", methods=["PUT"])
def remove_favorite_club(user_id: int, code: str):
    user = db.session.get(User, user_id)
    club = db.session.query(Club).filter_by(code=code).first()

    if user is None or club is None:
        return jsonify({"message": "User or Club not found"}), 404
    if club not in user.fav_clubs:
        return jsonify({"message": "Club not already favorited"}), 200

    user.fav_clubs.remove(club)
    club.favorites = max(0, club.favorites - 1)
    db.session.commit()
    return jsonify({"message": "Club removed from favorites"}), 200



# Modifies a club. The club's name, description, and tags can be modified. Modifying the club will replace the tags.
# The code cannot be modified since it's a unique identifier.
# If the request is not JSON, returns a 400 error.
# If the club is not found, returns a 404 error.
@app.route("/api/clubs/<string:code>", methods=["PUT"])
def modify_club(code: str):
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400
    club = db.session.query(Club).filter_by(code=code).first()
    if club is None:
        return jsonify({"message": "Club not found"}), 404

    data = request.get_json()
    if "name" in data and data["name"]:
        club.name = data["name"]
    if "description" in data and data["description"]:
        club.description = data["description"]
    if "tags" in data:
        club.tags = []
        for curr_tag in data['tags']:
            tag = db.session.query(Tag).filter_by(name=curr_tag).first()
            if not tag:
                tag = Tag(name=curr_tag)
                db.session.add(tag)
            club.tags.append(tag)
    db.session.commit()

    return jsonify({"message": "Club updated"}), 200


# Creates a new club with a code, name, description, and tags.
# If the request is not JSON, returns a 400 error.
# If the request does not contain code, name, description, and tags, returns a 400 error.
# If the club code already exists, returns a 400 error.
@app.route("/api/clubs", methods=["POST"])
def create_club():
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400
    data = request.get_json()
    required_fields = ["code", "name", "description", "tags"]
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Request must contain code, name, description, and tags"}), 400
    if db.session.query(Club).filter_by(code=data['code']).first() is not None:
        return jsonify({"message": "Club code is taken"}), 400

    club = Club(code=data['code'], name=data['name'], description=data['description'])
    db.session.add(club)
    tag_names = data['tags']
    existing_tags = Tag.query.filter(Tag.name.in_(tag_names)).all()
    existing_tag_names = [tag.name for tag in existing_tags]
    for tag_name in tag_names:
        if tag_name not in existing_tag_names:
            tag = Tag(name=tag_name)
            db.session.add(tag)
            club.tags.append(tag)
        else:
            club.tags.append(next(tag for tag in existing_tags if tag.name == tag_name))
    db.session.commit()

    return jsonify({"message": "Club added"}), 200


# Adds a comment to a club with the given code. This must not be a reply to another comment.
# If the request is not JSON, returns a 400 error.
# If the request does not contain a comment, returns a 400 error.
# If the club is not found, returns a 404 error.
@app.route("/api/users/<int:user_id>/clubs/<string:code>/comment", methods=["POST"])
def add_comment(user_id: int, code: str):
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400
    data = request.get_json()
    if "text" not in data:
        return jsonify({"message": "Request must contain text"}), 400

    club = db.session.get(Club, code)
    if club is None:
        return jsonify({"message": "Club not found"}), 404

    comment = ClubComments(user_id=user_id, club_id=club.id, text=data["text"])
    db.session.add(comment)
    db.session.commit()

    return jsonify({"message": "Comment added"}), 200

# Adds a comment to a club with the given code. This must be a reply to another comment.
# If the request is not JSON, returns a 400 error.
# If the request does not contain a comment, returns a 400 error.
# If the club is not found, returns a 404 error.
@app.route("/api/users/<int:user_id>/clubs/<string:code>/comment/<int:comment_id>", methods=["POST"])
def add_reply(user_id: int, code: str, comment_id: int):
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400
    data = request.get_json()
    if "text" not in data:
        return jsonify({"message": "Request must contain text"}), 400

    comment_to_reply = db.session.get(ClubComments, comment_id)
    club = comment_to_reply.club
    if club is None:
        return jsonify({"message": "Club not found"}), 404

    comment = ClubComments(user_id=user_id, club_id=club.id, text=data["text"], parent_comment_id=comment_id)
    db.session.add(comment)
    db.session.commit()

    return jsonify({"message": "Reply added"}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
