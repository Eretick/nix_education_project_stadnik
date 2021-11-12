""" App routes """
import os
from flask_app.app import films_app
from flask_app import models
from flask import jsonify

# main entrypoint
@films_app.route("/")
def index():
    return "200"


@films_app.route("/<string:name>")
def hello(name):
    return f"Hello, {name}!"


@films_app.route("/all_users/")
def all_users():
    return str(models.User.query.all())


@films_app.route("/<int:user_id>")
def user_by_id(user_id):
    return f"{models.User.query.filter_by(id=user_id).first()}"


@films_app.route("/find_film/<template>")
def find_film(template):
    """ Project requirement #1. Partial film search """
    films_data = models.Films.query.filter(models.Films.film_title.ilike("%"+template+"%")).all()
    return jsonify([film.to_dict() for film in films_data])
