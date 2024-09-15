from db import db
from functools import wraps
import jwt
from flask import request, abort, current_app, jsonify
from models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        if not token:
            return jsonify({
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }), 401
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = db.session.get(User, data["user_id"])
            if current_user is None:
                return jsonify({
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }), 401
        except jwt.ExpiredSignatureError:
            return jsonify({
                "message": "Authentication Token has expired!",
                "data": None,
                "error": "Unauthorized"
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "message": "Invalid Authentication Token!",
                "data": None,
                "error": "Unauthorized"
            }), 401
        except Exception as e:
            return jsonify({
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }), 500

        return f(current_user, *args, **kwargs)

    return decorated