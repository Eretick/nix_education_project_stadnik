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
@films_app.route("/find_film/<string:template>&<int:pagination_size>")
@films_app.route("/find_film/<string:template>&<int:pagination_size>&<int:page_number>")
def find_films(template, pagination_size=10, page_number=1):
    """ Project requirement #1. Partial film search. Project requirement #2. Pagination, 10 by default
    :param template: string film name partial match

    :param pagination_size: int size of pagination per 1 page

    :param page_number: integer number of search page

    :returns: list of found films json data.
    """
    if page_number == 1:
        page_offset = 0
    else:
        page_offset = pagination_size*(page_number-1)

    if template == "*":
        films_data = models.Films.query.limit(pagination_size).offset(page_offset).all()
    else:
        films_data = models.Films.query.filter(
            models.Films.film_title.ilike("%"+template+"%")).limit(pagination_size).offset(page_offset).all()
    return jsonify([film.to_dict() for film in films_data])
