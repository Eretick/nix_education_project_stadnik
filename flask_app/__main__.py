""" Main entry point. Useful for local launches. """
from flask_app.app import films_app
from flask_app import models
films_app.run()
