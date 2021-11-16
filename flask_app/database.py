""" Module for interacting with database """
from flask_login import current_user, login_required

from .errors import NotAuthenticatedError
from .models import *
from datetime import datetime


def validate_film(film: Films):
    """ Check if new film already in database

    :param film: Film db.Model instance which needs to compare with all films in database

    :returns True if film with same title, rate,
    """
    new_title = film.title
    new_user_id = film.user_id
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

        :param is_registered: bool guest mode, False is the guest, True is authorized. Default is False

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
        try:
            # Add director only if not in table already cause of unique column property
            db.session.add(director)
        # this is test error handling, will catch different errors during dev process.
        except Exception as e:
            print(e)
            db.session.rollback()
        else:
            db.session.commit()
            return director


def add_films_directors(film: Films, directors: list or str):
    """ Linking directors to films.

     :param list or str directors: list of directors names or string like 'director1,director2' who needs
                                    to be added to current film.

     :param film: Film instance which directors list is updating. Must be added to database in function calling moment.

     :returns None
     """
    if isinstance(directors, str):
        directors = directors.strip().split(",")
    elif directors is None:
        return
    else:
        if not isinstance(directors, list):
            raise TypeError("Wrong directors type!")
    # get list of all directors linked to film before
    print(film.id)
    added_directors = db.session.query(films_directors).filter_by(film_id=film.id).all()
    # adding every passed director
    for director_name in directors:
        add_director(full_name=director_name)
        # record to relation directors-films
        director = Directors.query.filter_by(full_name=director_name).first()
        # query.filter_by.all() from films_directors table makes dicts (film_key, director_key)
        # creating the same for detecting duplicates
        current_pair = film.id, director.id
        print(added_directors, current_pair, current_pair not in added_directors)
        if current_pair not in added_directors:
            director.films.append(film)


def add_genre(genre_name: str):
    """ Add film's genre row in Genres db table

    :param genre_name: string name

    :returns None if commit is True else Genre
    """
    genre = Genres(name=genre_name)
    all_genres = [i.name for i in Genres.query.all()]
    # Add genre only if not in table already cause of unique column property
    if genre_name not in all_genres:
        # trying to add genre to table
        try:
            db.session.add(genre)
        # this is test error handling, will catch different errors during dev process.
        except Exception as e:
            print(e)
            db.session.rollback()
        else:
            db.session.commit()
    else:
        raise ValueError(f"Genre {genre_name}  already exists!")


def add_film(title: str, release_date: datetime, user: int or User,
             directors: str or list, genres: list, description: str = None,
             rate: int = 0, poster_url: str = "https://"):
    """ Create film row in database and add row to Films table in db.

    :param title: string film name

    :param release_date: datetime type release time. As example, datetime.datetime(1996, 1, 19)

    :param user: unique integer id of user who added film. Also can be User instance

    :param directors: str name, goes to directors table

    :param description string, default is None

    :param rate integer from 0 to 10 including, default is 10.

    :param poster_url: string of film's url poster

    :param genres: string with ganres names devided by space. Goes to the relation table

    :returns None
    """
    if isinstance(user, User):
        user_id = User.id
    elif isinstance(user, str):
        user_id = int(user)
        user = User.query.all()[user_id-1]
    elif isinstance(user, int):
        user_id = user
        user = User.query.all()[user_id - 1]
    else:
        raise TypeError("User id must be an integer, or numeric string or User instance!")

    film = Films(title=title, description=description,
                 user_id=int(user_id), rate=float(rate), release_date=release_date, poster_url=poster_url)

    if validate_film(film) is not True:
        try:
            # trying to add new film to db table
            db.session.add(film)
            #print(f"Adding film {film.title}")
        # this is test error handling, will catch different errors during dev process.
        except Exception as e:
            print(e)
            print(f"Error adding film {film.title}")
            db.session.rollback()
        else:

            db.session.commit()
            # if films inserted successfully, inserting everything else
            # making record to directors table
            add_films_directors(film, directors)
            # record to relation users-films table
            user.films.append(film)
            # recording to genres relations table
            genres = genres.strip().split()
            for genre in genres:
                # looking for genres instances in genres table
                # for adding relations with films
                genre_instance = Genres.query.filter_by(name=genre).first()
                if genre_instance is None:
                    genre_instance = Genres(name=genre)
                genre_instance.films.append(film)
            # confirm changes
            return film
    else:
        raise TypeError(f"Film {film.title} already added.")


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

    :param genres: string with genres names devided by space. Goes to the relation table

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
                #film.set_genres(genres)
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
        print(film)
        db.session.commit()
        return film, 200
    else:
        raise TypeError("ID must be int!")
