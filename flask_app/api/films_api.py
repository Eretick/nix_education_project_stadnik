""" Api for general things """
from datetime import datetime
from flask_login import login_required, current_user
from flask_restx import Resource, fields, reqparse
from flask_app import database, models
from flask_app.app import films_api
# models
from flask_app.errors import NotAuthenticatedError, UserPermissionError

film_model = films_api.model("Film", {"id": fields.Integer(required=True),
                                      "title": fields.String(required=True),
                                      "description": fields.String(required=True),
                                      "rate": fields.Float(required=True),
                                      "genres": fields.List(fields.String),
                                      "directors": fields.List(fields.String),
                                      "release_date": fields.String(required=True),
                                      "poster_url": fields.String(required=True),
                                      "user_id": fields.Integer(required=True)})


@films_api.route("/api/films/")
class FilmsManipulator(Resource):
    """ Resource class for filtering films. """

    @films_api.marshal_with(film_model, code=200, envelope="films")
    @films_api.doc(params={"template": "film name partial match",
                           "pagination_size": "size of pagination per 1 page",
                           "page_number": "number of search page",
                           "date_from": "data in %Y.%m.%d format. Discarding films before given date's year",
                           "date_to": "data in %Y.%m.%d format. Discarding films after given date's year",
                           "directors": "(optional) list of directors for filtering",
                           "genres": "(optional) list of genres for filtering",
                           "sort_by": "(optional) sorting mode 'rate', 'date' or None. None is Default",
                           "sort_type": "(optional) sorting type 'desc', 'asc'. None is Default"
                           })
    def get(self):
        """ Film search with pagination, 10 items by default.
        :returns Films list which match search parameters or 404
        """
        # parsing the GET params
        parser = reqparse.RequestParser()
        parser.add_argument("template")
        parser.add_argument("page_number", type=int, help="Integer number of viewing page.")
        parser.add_argument("pagination_size", type=int, help="Count of items on 1 page.")
        parser.add_argument("date_from", help="Beginning of dates filter range. ")
        parser.add_argument("date_to", help="End of dates filter range. ")
        parser.add_argument("genres", help="List of genres for filter. ")
        parser.add_argument("directors", help="List of genres for filter. ")
        parser.add_argument("sort_by", help="sorting mode 'rate', 'date' or None. None is Default.")
        parser.add_argument("sort_type", help="sorting mode 'asc' (ascending) or 'desc' (descending). 'asc' is Default")
        params = parser.parse_args()
        # fix params if not in GET
        pagination_size = 10 if params["pagination_size"] is None else params["pagination_size"]
        page_number = 1 if params["page_number"] is None else int(params["page_number"])
        template = "" if params["template"] is None else params["template"]
        date_from = params["date_from"] if params["date_from"] is not None else None
        date_to = params["date_to"] if params["date_to"] is not None else None
        genres = params["genres"] if params["genres"] is not None else None
        directors = params["directors"] if params["directors"] is not None else None
        sort_by = params["sort_by"] if params["sort_by"] is not None else None
        sort_type = params["sort_type"] if params["sort_type"] is not None else None

        # filtering all films by all possible args.
        # partial range (only from/only to some date) also supported
        try:
            films_data = database.find_films_by_filters(template=template, date_from=date_from, date_to=date_to,
                                                    page_number=page_number, pagination_size=pagination_size,
                                                    genres=genres, directors=directors, sort_by=sort_by, sort_type=sort_type)
        except ValueError as e:
            return str(e), 403

        return films_data, 200

    #@films_api.marshal_with(film_model, code=201, envelope="films")
    @films_api.doc(params={"title": "string title of the film",
                           "description": " string film description",
                           "directors": "film director/directors divided by ',' ",
                           "rate": "integer from 0 to 10 including, default is 10.",
                           "date": "datetime type release time. As example, datetime.datetime(1996, 1, 19)",
                           "poster_url": "string of film's url poster",
                           "genres": "datetime type release time. As example, datetime.datetime(1996, 1, 19)",
                           })
    @login_required
    def post(self):
        """ Adding new film to Films database table. Only for logged in users. """
        # parsing params
        parser = reqparse.RequestParser()
        parser.add_argument("title", required=True)
        parser.add_argument("description")
        parser.add_argument("directors", required=True)
        parser.add_argument("date", type=str, help="Date must be passed as string like 2010.10.10", required=True)
        parser.add_argument("poster_url", type=str)
        parser.add_argument("genres", required=True)
        parser.add_argument("rate", type=int, help="Integer number of film's rate between 1-10.")
        params = parser.parse_args()
        print(params)
        # fix params if not in GET
        title = params["title"]
        description = params["description"]
        directors = params["directors"]
        print(directors)
        # incoming date must be in string type like 2010.10.10 format
        date = datetime.strptime(params["date"], "%Y.%m.%d") if params["date"] is not None else None
        poster_url = params["poster_url"]
        genres = params["genres"]
        rate = 0 if params["rate"] is None else params["rate"]
        # aborting operation if one of important params wasn't passed
        if None in [title, description, directors, date, poster_url, genres]:
            return "Not all film's parameters passed!", 403
        # only registered users can add the films
        if current_user.is_authenticated:
            # getting all film's passed directors
            directors = [i for i in directors.split(",") if i != ""]
            # TODO: delete choosing first element then  multi-directors support will be added
            try:
                film = database.add_film(title=title, description=description,
                                         release_date=date, user=current_user.id,
                                         directors=directors, rate=rate,
                                         poster_url=poster_url, genres=genres)
            except ValueError:
                return "Current film already exists!", 403
            return film.to_dict(), 201

    @films_api.marshal_with(film_model, code=200, envelope="films")
    @films_api.doc(params={"id": "id of film you want to delete."})
    @login_required
    def delete(self):
        """ Delete method for film, passed as id parameter.
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
    @films_api.doc(params={"id": "film's id from database you want to edit",
                           "title": "(optional) string title of the film",
                           "description": "(optional) string film description",
                           "directors": "(optional) film director/directors decided by ',' ",
                           "rate": "(optional) integer from 0 to 10 including, default is 10.",
                           "date": "(optional) datetime type release time. "
                                   "As example, datetime.datetime(1996, 1, 19)",
                           "poster_url": "(optional) string of film's url poster",
                           "genres": "string with genres names decided by ',' "
                           })
    @login_required
    def put(self):
        """ Film's edition """
        parser = reqparse.RequestParser()
        parser.add_argument("id", required=True, help="Film's id")
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
