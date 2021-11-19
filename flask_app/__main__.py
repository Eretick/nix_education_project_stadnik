""" Main entry point. Useful for local launches. """
from flask_app import app
from flask_app import models
from flask_app import database
import flask_app.api.films_api
import flask_app.api.users_api
app.films_app.run()