# is not null in query.filter(User.name.isnot(None))
import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# create and setup films_app

films_app = Flask(__name__)
films_app.config.from_mapping(SECRET_KEY=os.environ.get('SECRET_KEY', default='dev'),
                              SQLALCHEMY_TRACK_MODIFICATIONS=False,
                              SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI',
                                                                     default='sqlite:///db.db',
                                                                     #default="postgresql://vladislav:my_password@localhost:5432/postgres",
                                                                     ),
                              DEBUG=True)
db = SQLAlchemy(films_app)
migrate = Migrate(films_app, db)

# import from top of module create circular import of films_app instance

from flask_app.routes import *
