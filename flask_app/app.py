import os
from flask import Flask
from flask_login import LoginManager
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# create and setup films_app

films_app = Flask(__name__)
films_app.config.from_mapping(SECRET_KEY=os.environ.get('SECRET_KEY', default='dev'),
                              SQLALCHEMY_TRACK_MODIFICATIONS=False,
                              SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI',
                                                                     default="postgresql://vladislav:my_password@localhost:5432/postgres",
                                                                     ),
                              # DEBUG=True,
                              )
# for database
db = SQLAlchemy(films_app)
# for login
login_manager = LoginManager(films_app)
login_manager.init_app(films_app)
# for api
films_api = Api(films_app, doc="/api/")
# for db migrations
migrate = Migrate(films_app, db)
