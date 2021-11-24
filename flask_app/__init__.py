""" Main entry point. Useful for local launches. """
from flask_app.app import films_app
from flask_app.api import films_api
films_app.run()