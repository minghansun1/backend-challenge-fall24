from db import db
from werkzeug.security import generate_password_hash, check_password_hash


# Defines the association table for a many-to-many relationship between clubs and tags
clubs_to_tags = db.Table('clubs_to_tags',
                         db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True),
                         db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
                         db.Index('index_clubs_to_tags', 'club_id', 'tag_id')
                         )

# Defines the association table for a many-to-many relationship between users and clubs they've favorited
user_to_favorite_club = db.Table('user_to_favorite_club',
                                 db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                                 db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True),
                                 db.Index('index_users_to_club', 'user_id', 'club_id')
                                 )


# Each model has a column for a unique id, which makes searching and comparing inside a model more efficient.
# Additionally, each model has a to_dict method, which returns a dictionary representation of the model's data.
# This is useful for converting the model to a JSON object during API calls

# Defines the Club model. Includes a table of values for the club's code, name, description, and tags.
class Club(db.Model):
    __tablename__ = 'club'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    favorites = db.Column(db.Integer, default=0)

    tags = db.relationship('Tag', secondary=clubs_to_tags, back_populates='clubs')
    users = db.relationship('User', secondary=user_to_favorite_club, back_populates='fav_clubs')
    comments = db.relationship('Comment', back_populates='club')

    def to_dict(self):
        return {
            "id": self.id, 
            "code": self.code, 
            "name": self.name, 
            "description": self.description, 
            "tags": [tag.name for tag in self.tags], 
            "favorites": self.favorites
        }

# Defines the Tag model. Includes a table of values for the tag's name and the clubs associated with the tag.

class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    clubs = db.relationship('Club', secondary=clubs_to_tags, back_populates='tags')

    def to_dict(self):
        return {"name": self.name, "clubs": [club.name for club in self.clubs]}


# Defines the User model. Includes a table of values for the user's username, email,
# password, first name, last name, school, major, graduation year, and favorite clubs.
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    school = db.Column(db.String(80), nullable=False)
    major = db.Column(db.String(80), nullable=False)
    grad_year = db.Column(db.Integer, nullable=False)
    
    fav_clubs = db.relationship('Club', secondary=user_to_favorite_club, back_populates='users')
    comments = db.relationship('Comment', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_public_dict(self):
        return {"id": self.id, 
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name, 
            "last_name": self.last_name,
            "school": self.school, 
            "major": self.major, 
            "grad_year": self.grad_year,
        }
    
    def to_private_dict(self):
        return {"id": self.id, 
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "first_name": self.first_name, 
            "last_name": self.last_name,
            "school": self.school, 
            "major": self.major, 
            "grad_year": self.grad_year,
            "fav_clubs": [club.name for club in self.fav_clubs]
        }
    
# Defines the Comment model. Includes a table of values for the 
# comment's user, club, parent comment, text, and timestamp.
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='comments')
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    club = db.relationship('Club', back_populates='comments')
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    parent_comment = db.relationship('Comment', remote_side=[id], backref='replies')
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "club": self.club.name,
            "parent_comment_id": self.parent_comment_id,
            "text": self.text,
            "timestamp": self.timestamp
        }