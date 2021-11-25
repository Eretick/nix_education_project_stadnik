""" Module for interacting with database """
from flask_login import current_user
from sqlalchemy import func, and_, desc, asc
from .errors import NotAuthenticatedError, NotFoundError
from .models import *
from datetime import datetime


def minimal_films_date(to_string=False, decrease=True):
    """ Function for getting minimal films date from

    :param bool decrease: optional fix minimal date by 1 year cause of films with given year
                         not matching in >= expression

    :param bool to_string: optional convert given datetime value to string

    """
    min_date = db.session.query(func.min(Films.release_date)).first()[0]
    if min_date is None:
        raise NotFoundError("Films dates are empty!")
    if decrease:
        min_date = min_date.replace(year=min_date.year - 1)
    if to_string:
        min_date = datetime.strftime(min_date, "%Y.%m.%d")
    return min_date


def maximum_films_date(to_string=False):
    """ Function for getting minimal films date from """
    max_date = db.session.query(func.max(Films.release_date)).first()[0]
    if max_date is None:
        raise NotFoundError("Films dates are empty!")
    if to_string:
        max_date = datetime.strftime(max_date, "%Y.%m.%d")
    return max_date


def find_films_by_filters(template: str = None, date_from: datetime or str = None, date_to: datetime or str = None,
                          page_number: int = None, pagination_size: int = None, genres: list = None,
                          directors: list = None, sort_by: str = None, sort_type: str = None):
    """ Filtering films by passed parameters.

    :param str template: (optional) film name partial match

    :param int pagination_size: (optional) size of pagination per 1 page

    :param int page_number: (optional) number of search page

    :param str genres: (optional) list of genres for filtering

    :param str directors: (optional) list of directors for filtering

    :param str date_from: (optional) data in "%Y.%m.%d" format. Discarding films before given date's year

    :param str date_to: (optional) data in "%Y.%m.%d" format. Discarding films after given date's year

    :param str sort_by: (optional) sorting mode 'rate', 'date' or None. None is Default

    :param str sort_type: (optional) sorting mode 'asc' (ascending) or 'desc' (descending). None is Default

    :returns: list of found films json data and status 200 if found, else error with status 404

    """
    # finding min/max dates in out database for searching by all films by default
    if sort_by not in ["rate", "date", None]:
        raise ValueError("Argument sort_by can has only 'rate', 'date' or None values! ")
    if sort_type not in ["asc", "desc", None]:
        raise ValueError("Argument sort_by can has only 'asc', 'desc' or None values! ")
    if date_from is None:
        date_from = minimal_films_date(to_string=True, decrease=True)
    if date_to is None:
        date_to = maximum_films_date(to_string=True)
    if genres is None:
        genres = [genre.name for genre in Genres.query.all()]
    elif isinstance(genres, str):
        genres = genres.split(",")
    if directors is None:
        directors = [director.full_name for director in Directors.query.all()]
    elif isinstance(directors, str):
        directors = directors.split(",")

    page_offset = 0 if page_number == 1 else pagination_size * (page_number - 1)
    # making search
    films_data = db.session.query(Films).filter(Films.title.ilike("%" + template + "%")).filter(
        and_(Films.release_date >= date_from)).filter(and_(Films.release_date <= date_to)).join(films_directors)\
        .filter(Films.id == films_directors.c.film_id).join(Directors).filter(Directors.full_name.in_(directors))\
        .join(films_genres).filter(Films.id == films_genres.c.film_id).join(Genres).filter(Genres.name.in_(genres)) \

    # defining sorting type
    if sort_type is not None:
        if sort_type == "asc":
            sorting = asc
        elif sort_type == "desc":
            sorting = desc
    else:
        sorting = asc

    if sort_by is not None:
        if sort_by == "rate":
            column = Films.rate
        elif sort_by == "date":
            column = Films.release_date
    else:
        column = Films.id

    films_data = films_data.order_by(sorting(column))
    # adding limits
    films_data = films_data.limit(pagination_size).offset(page_offset)

    # if films wasn't found
    if len(films_data.all()) == 0:
        raise NotFoundError()
    return films_data.all()


def validate_film(film: Films):
    """ Check if new film already in database

    :param film: Film db.Model instance which needs to compare with all films in database

    :returns True if film with same title, rate,
    """
    new_title = film.title
    new_date = film.release_date
    # TODO: add to check directors list also
    search = Films.query.filter_by(title=new_title,
                                   release_date=new_date
                                   ).first()
    if search is not None:
        return True
    return False


def add_user(nickname: str, email: str, password: str, country: str = "",
             city: str = "", street: str = "", is_admin: bool = False):
    """ Create user row in database and add row to User table in db.

        :param nickname: string authorized user's unique name, default is None for guests.

        :param email: string authorized user's unique email, default is None for guests.

        :param password: string user password

        :param country string authorized user's county, default is None for guests.

        :param city string authorized user's city, default is None for guests.

        :param street string authorized user's street, default is None for guests.

        :param is_admin bool admin mode for authorized users.

        :returns None
    """
    # creating registered or guest user
    user = User(nickname=nickname, email=email, password=password,
                country=country, city=city, street=street, is_admin=is_admin)
    # Add genre only if not in table already cause of unique column property
    # trying to add user to base
    all_emails = [i.email for i in User.query.all()]
    if email not in all_emails:
        db.session.add(user)
        db.session.commit()

    else:
        raise ValueError("User with same email already registered")


def add_director(full_name: str):
    """ Add film's director row in database

    :param full_name: string name

    :returns Director instance if found, else None
    """
    director = Directors(full_name=full_name)
    all_directors = [i.full_name for i in Directors.query.all()]
    # trying to add director to base
    if full_name not in all_directors:
        db.session.add(director)
        db.session.commit()
    return director



def delete_director(director: str or Directors):
    """ Function for deleting film's director.
    Also changes film's deleted director to "unknown" value if given director is only one in film's
    directors list.

    :param str director: name of director you need to delete.
                        Also can be Director instance in case of internal using
    """
    if isinstance(director, Directors):
        director_id = director.id
    elif isinstance(director, str):
        director_db = Directors.query.filter_by(full_name=director).first()
        if director_db is not None:
            director_id = director_db.id
        else:
            raise NotFoundError()
    else:
        raise TypeError("Argument director must be string name or Director instance!")

    # find all records in films_directors relation table with director we wanna delete
    # get the list of tuples with 2 elements, 1st is film_id, 2nd is director id
    all_deleting = db.session.query(films_directors).filter(films_directors.c.director_id == director_id)
    # if films are linked to current director:
    deleting_list = all_deleting.all()
    count_rows = len(deleting_list)
    if count_rows > 0:
        # find out if deleting director is the last one
        films_list = [row[0] for row in all_deleting]
        for i, film_id in enumerate(films_list):
            directors = Films.query.filter_by(id=film_id).first().directors
            # if deleting director is not only one director in film's directors list
            # simply delete the row from directors relation table
            if len(directors) > 1:
                cond1 = (films_directors.c.film_id == deleting_list[i][0])
                cond2 = (films_directors.c.director_id == deleting_list[i][1])
                all_deleting.filter(cond1 & cond2).delete()
            # if it the last one, just change the row director link to id 1 ("unknown")"
            elif len(directors) == 1:
                cond1 = (films_directors.c.film_id == deleting_list[i][0])
                cond2 = (films_directors.c.director_id == deleting_list[i][1])
                all_deleting.filter(cond1 & cond2).update({"director_id": 1})
    # finally delete director from directors table
    Directors.query.filter_by(id=director_id).delete()
    db.session.commit()
    return f"Director {director} deleted successfully.", 200


def add_genre(genre_name: str):
    """ Add film's genre row in Genres db table

    :param genre_name: string name

    :returns None if commit is True else Genre
    """
    genre = Genres(name=genre_name.strip())
    all_genres = [i.name.strip() for i in Genres.query.all()]
    # Add genre only if not in table already cause of unique column property
    if genre_name.strip() not in all_genres:
        # trying to add genre to table
        db.session.add(genre)
        db.session.commit()
    else:
        raise ValueError(f"Genre {genre_name}  already exists!")


def add_films_directors(film: Films, directors: list or str):
    """ Linking directors to films.

     :param list or str directors: list of directors names or string like 'director1,director2' who needs
                                    to be added to current film.

     :param film: Film instance which directors list is updating. Must be added to database in function calling moment.

     :returns None
     """
    if isinstance(directors, str):
        directors = [i.strip() for i in directors.strip().split(",")]
    elif directors is None:
        return
    else:
        if not isinstance(directors, list):
            raise TypeError("Wrong directors type!")

    # get list of all directors linked to film before (rows film_id, director_id)
    added_directors = db.session.query(films_directors).filter_by(film_id=film.id).all()
    # if Directors table has data
    if added_directors:
        # get the same list but as Director instances
        added_directors2 = [i.full_name for i in film.directors]
        # deleting "unknown" value from relation table for current film
        if "unknown" in added_directors2:
            index = added_directors2.index("unknown")
            cond1 = (films_directors.c.film_id == added_directors[index][0])
            cond2 = (films_directors.c.director_id == added_directors[index][1])
            db.session.query(films_directors).filter(cond1 & cond2).delete()

    # adding every passed director
    for director_name in directors:
        add_director(full_name=director_name)
        # record to relation directors-films
        director = Directors.query.filter_by(full_name=director_name).first()
        # query.filter_by.all() from films_directors table makes dicts (film_key, director_key)
        # creating the same for detecting duplicates
        current_pair = film.id, director.id
        if current_pair not in added_directors:
            director.films.append(film)


def add_films_genres(film: Films, genres: list or str):
    """ Linking genres to film.

     :param list or str genres: list of directors names or string like 'director1,director2' who needs
                                    to be added to current film. Every time needs full list cause old values will
                                    be deleted.

     :param film: Film instance which directors list is updating. Must be added to database in function calling moment.

     :returns None
     """
    if isinstance(genres, str):
        genres = genres.strip().split(",")
    elif genres is None:
        return
    else:
        if not isinstance(genres, list):
            raise TypeError("Wrong directors type!")

    added_genres = db.session.query(films_genres).filter_by(film_id=film.id).all()
    # deleting old added genres
    db.session.query(films_genres).filter_by(film_id=film.id).delete()
    db.session.commit()
    for genre in genres:
        # looking for genres instances in genres table
        # for adding relations with films
        genre_instance = Genres.query.filter_by(name=genre.rstrip()).first()
        # if genres table doesn't have current genre, add it
        if genre_instance is None:
            genre_instance = Genres(name=genre.strip())
            db.session.add(genre_instance)
            db.session.commit()
            genre_instance = Genres.query.filter_by(name=genre.rstrip()).first()
        # avoid adding duplicates
        current_pair = film.id, genre_instance.id
        if current_pair not in added_genres:
            genre_instance.films.append(film)


def add_film(title: str, release_date: datetime, user: int or User,
             directors: str or list, genres: str or list, description: str = None,
             rate: int = 0, poster_url: str = "https://"):
    """ Create film row in database and add row to Films table in db.

    :param title: string film name

    :param release_date: datetime type release time. As example, datetime.datetime(1996, 1, 19)

    :param user: unique integer id of user who added film. Also can be User instance

    :param directors: str name, goes to directors table

    :param description string, default is None

    :param rate integer from 0 to 10 including, default is 10.

    :param poster_url: string of film's url poster

    :param genres: string with genres names decided by space. Goes to the relation table

    :returns None
    """
    if isinstance(user, User):
        user_id = User.id
    elif isinstance(user, str):
        user_id = int(user)
        user = User.query.all()[user_id - 1]
    elif isinstance(user, int):
        user_id = user
        user = User.query.all()[user_id - 1]
    else:
        raise TypeError("User id must be an integer, or numeric string or User instance!")

    film = Films(title=title, description=description,
                 user_id=int(user_id), rate=float(rate), release_date=release_date, poster_url=poster_url)

    if validate_film(film) is not True:

        # trying to add new film to db table
        db.session.add(film)
        db.session.commit()
        # find added film again from db for getting id
        film = Films.query.filter_by(title=title, description=description, user_id=int(user_id),
                                     rate=float(rate), release_date=release_date, poster_url=poster_url).first()

        # if films inserted successfully, inserting everything else
        # making record to directors table
        add_films_directors(film, directors)
        # record to relation users-films table
        user.films.append(film)
        # recording to genres relations table
        add_films_genres(film, genres)
        db.session.commit()
        # confirm changes
        return film
    else:
        raise ValueError(f"Film {film.title} already added.")


def edit_film(id: int, title: str = None, release_data: datetime = None,
              directors: str = None, genres: list = None, poster_url: str = None, description: str = None,
              rate: int = 0):
    """ Create film row in database and add row to Films table in db.

    :param int id: film's id from database what needs to be updated.

    :param title: string film name

    :param release_data: datetime type release time. As example, datetime.datetime(1996, 1, 19)

    :param directors: str/list name/s, goes to directors table

    :param description string, default is None

    :param rate integer from 0 to 10 including, default is 10.

    :param poster_url: string of film's url poster

    :param genres: string with genres names divided by space. Goes to the relation table

    :returns None
    """
    # Looking at film with given id
    if isinstance(directors, str):
        directors = directors.strip().split(",")
    film = Films.query.filter_by(id=id).first()
    user = current_user
    if current_user.is_authenticated:
        # if film was found
        if film:
            # if user has rights to edit films
            if user.is_admin or film.user_id == user.id:
                film.set_title(title)
                film.set_description(description)
                # making record to directors table
                add_films_directors(film, directors)
                film.set_rate(rate)
                film.set_release_date(release_data)
                film.set_poster_url(poster_url)
                add_films_genres(film, genres)
                db.session.commit()
                return film.to_dict(), 200
            else:
                raise ValueError("Only admins and owners can edit film!")
        else:
            return "Film not found", 200
    else:
        return NotAuthenticatedError()


def delete_film(id: int):
    """ Function for deleting the film from all films table """
    if isinstance(id, int):
        film = Films.query.filter_by(id=id).delete()
        db.session.commit()
        return film, 200
    else:
        raise TypeError("ID must be int!")


