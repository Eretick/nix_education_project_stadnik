""" Api for general things """
import json
from datetime import datetime

from flask import jsonify, Response, make_response, request
from flask_login import login_required, current_user
from flask_restx import Resource, Api, fields, reqparse

import flask_app.app
from flask_app import database
from flask_app.app import films_api, models


# models
from flask_app.errors import NotAuthenticatedError, UserPermissionError

film_model = films_api.model("Film", {"id": fields.Integer(required=True),
                                      "title": fields.String(required=True),
                                      "description": fields.String(required=True),
                                      "rate": fields.Float(required=True),
                                      "release_date": fields.String(required=True),
                                      "poster_url": fields.String(required=True),
                                      "user_id": fields.Integer(required=True)})


@films_api.route("/api/films/")
class FilmsManipulator(Resource):
    """ Resource class for filtering films. """
    @films_api.marshal_with(film_model, code=200, envelope="films")
    def get(self):
        """ Partial film search with pagination, 10 items by default.
    Parameters:

        :param template: string film name partial match

        :param pagination_size: int size of pagination per 1 page

        :param page_number: integer number of search page

        :returns: list of found films json data and status 200 if found, else status 404
        """
        # parsing the GET params
        parser = reqparse.RequestParser()
        parser.add_argument("template")
        parser.add_argument("page_number", type=int, help="Integer number of viewing page.")
        parser.add_argument("pagination_size", type=int, help="Count of items on 1 page.")
        params = parser.parse_args()
        # fix params if not in GET
        pagination_size = 10 if params["pagination_size"] is None else params["pagination_size"]
        page_number = 1 if params["page_number"] is None else int(params["page_number"])
        template = None if params["template"] is None else params["template"]
        page_offset = 0 if page_number == 1 else pagination_size*(page_number-1)
        # getting films from database
        if template is None:
            films_data = models.Films.query.limit(pagination_size).offset(page_offset).all()
        else:
            films_data = models.Films.query.filter(
                models.Films.title.ilike("%"+template+"%")).limit(pagination_size).offset(page_offset).all()
            if films_data is []:
                return "Films not found", 404
        return films_data, 200

    @films_api.marshal_with(film_model, code=201, envelope="films")
    def post(self):
        """ Adding new film to Films database table. Only for logged in users.
        USE IT IN YOUR routes.py WITH @login_required DECORATOR!

            :param title: string title of the film

            :param description: film description

            :param director: film director/directors devided by ","

            :param rate integer from 0 to 10 including, default is 10.

            :param date: datetime type release time. As example, datetime.datetime(1996, 1, 19)

            :param logo_url: string of film's url poster

            :param genres: string with ganres names devided by ","

            :returns code, 201 if created successfully (look for database.add_film method)
        """
        # parsing params
        parser = reqparse.RequestParser()
        parser.add_argument("title")
        parser.add_argument("description")
        parser.add_argument("directors")
        parser.add_argument("date", type=str, help="Date must be passed as string like 2010.10.10")
        parser.add_argument("poster_url", type=str)
        parser.add_argument("genres")
        parser.add_argument("rate", type=int, help="Integer number of film's rate between 1-10.")
        params = parser.parse_args()
        # fix params if not in GET
        title = params["title"]
        description = params["description"]
        directors = params["directors"]
        # incoming date must be in string type like 2010.10.10 format
        date = datetime.strptime(params["date"], "%Y.%m.%d") if params["date"] is not None else None
        logo_url = params["poster_url"]
        genres = params["genres"]
        rate = 0 if params["rate"] is None else params["rate"]
        # aborting operation if one of important params wasn't passed
        if None in [title, description, directors, date, logo_url, genres]:
            return "Not all film's parameters passed!", 403
        # only registered users can add the films
        if current_user.is_authenticated:
            # getting all film's passed directors
            directors = [i for i in directors.split(",") if i != ""]
            # TODO: delete choosing first element then  multi-directors support will be added
            film = database.add_film(title=title, description=description,
                                     release_date=date,
                                     user=current_user.id, directors=directors, rate=rate,
                                     poster_url=logo_url, genres=genres)
            return film.to_dict(), 201

    @films_api.marshal_with(film_model, code=200, envelope="films")
    def delete(self):
        """ Delete method for film, passed as id parameter.
        :param int id: id of film you want to delete.

        :returns deleted film and status 200 if successes.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("id", type=int, help="Integer number of id in films database table.")
        params = parser.parse_args()
        film_id = params.get("id")
        if current_user.is_authenticated:
            if current_user.is_admin or current_user.id == film_id:
                if film_id is not None:
                    film = models.Films.query.filter_by(id=film_id).first()
                    if film is not None:
                        deleted_film = database.delete_film(film_id)
                        return deleted_film, 200
                    else:
                        return "Film with given id doesn't exist in films database", 404
                else:
                    return "Wrong deletion film id!", 404
            else:
                raise UserPermissionError("You must be login for deleting film!")
        else:
            raise NotAuthenticatedError("You must be login for deleting film!")

    @films_api.marshal_with(film_model, code=201, envelope="edited_film")
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument("id")
        parser.add_argument("title")
        parser.add_argument("description")
        parser.add_argument("directors")
        parser.add_argument("date")
        parser.add_argument("poster_url")
        parser.add_argument("genres")
        parser.add_argument("rate", type=int, help="Integer number of film's rate between 1-10.")
        params = parser.parse_args()

        id = params["id"]
        title = params["title"]
        description = params["description"]
        directors = params["directors"]
        date = params["date"]
        logo_url = params["poster_url"]
        genres = params["genres"]
        rate = params["rate"]

        edition = database.edit_film(id=id, title=title, description=description,
                                     directors=directors, rate=rate, release_data=date,
                                     poster_url=logo_url, genres=genres)
        return edition, 200


