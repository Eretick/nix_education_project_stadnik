from flask_login import current_user, login_user, logout_user, login_required
from flask_app.models import User
from flask_app.app import films_api
from flask_restx import Resource, fields, reqparse
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
            return user, 200
        else:
            return "You must login for view profile", 401


@films_api.route("/api/users/login/")
class UserLogin(Resource):
    @films_api.marshal_with(user_model, code=200, envelope="users")
    @films_api.doc(params={"email": "string user's email",
                           "password": "string user's password"
                           })
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", required=True)
        parser.add_argument("password", required=True)
        params = parser.parse_args()

        email = params["email"]
        password = params["password"]
        if email is None or password is None:
            return "No data passed", 403

        if current_user.is_authenticated:
            return f"{current_user.nickname} already logged in!", 200

        user = User.query.filter_by(email=email).first()
        if user is not None and user.check_password(password):
            login_user(user, remember=True)
            return user.to_dict(), 200
        return "Wrong email/password pair", 204


@films_api.route("/api/users/logout/")
class UserLogout(Resource):
    @login_required
    def get(self):
        if current_user.is_authenticated:
            message = f"User {current_user.nickname} logged out"
            logout_user()
            return message
        else:
            raise NotAuthenticatedError("Only logged in users can logout!", status_code=200)