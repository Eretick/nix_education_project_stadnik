""" Main entry point. Useful for local launches. """
from flask_app.app import films_app
from flask_app import models
import flask_app.api.films_api
import flask_app.api.users_api
films_app.run()
