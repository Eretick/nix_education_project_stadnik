from flask import jsonify
from flask_login import current_user, login_user, logout_user

from flask_app import database
from flask_app.app import films_app, films_api, models
from flask_restx import Resource, Api, fields, reqparse

from flask_app.errors import NotAuthenticatedError

user_model = films_api.model("User", {"id": fields.Integer(), "nickname": fields.String(),
                                      "email": fields.String(), "country": fields.String(),
                                      "city": fields.String(), "street": fields.String(),
                                      "is_admin": fields.Boolean()})


@films_api.route("/api/users/profile/")
class UserProfile(Resource):
    @films_api.marshal_with(user_model, code=200, envelope="users")
    def get(self):
        """
        Registered current user profile
        """
        if current_user.is_authenticated:
            user = current_user.to_dict()
            #return jsonify(user), 200
            return user, 200
        else:
            return "You must login for view profile", 401


@films_api.route("/api/users/login/")
class UserLogin(Resource):
    @films_api.marshal_with(user_model, code=200, envelope="users")
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email")
        parser.add_argument("password")
        params = parser.parse_args()

        email = params["email"]
        password = params["password"]
        if email is not None or password is not None:
            if current_user.is_authenticated:
                return f"{current_user.nickname} already logged in!", 200
            else:
                user = models.User.query.filter_by(email=email).first()
                if user is not None:
                    if user.check_password(password):
                        login_user(user, remember=True)
                        return f"Hi, {user.nickname}!", 200
                    else:
                        return "Wrong email/password pair", 204
                else:
                    return "User not found", 200
        else:
            return "No data passed", 200


@films_api.route("/api/users/logout/")
class UserLogout(Resource):
    @films_api.marshal_with(user_model, code=200, envelope="users")
    def get(self):
        if current_user.is_authenticated:
            logout_user()
            return current_user.to_dict(), 200
        return NotAuthenticatedError("Only logged in users can logout!", status_code=200)
