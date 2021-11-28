""" Main films_app package entrypoint  """
import os
from flask import Flask
from flask_login import LoginManager
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
# for login
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    """ Films_app factory function """
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY=os.environ.get('SECRET_KEY', default='dev'),
                                  SQLALCHEMY_TRACK_MODIFICATIONS=False,
                                  SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI'))
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    app.app_context().push()
    return app


films_app = create_app()
films_api = Api(films_app, doc="/api/", title="Stadnik's 'Films Library' API")
