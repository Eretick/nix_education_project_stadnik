""" Module for interacting with database """
from .models import *
from datetime import datetime


def validate_film(film: Films):
    """ Check if new film already in database

    :param film: Film db.Model instance which needs to compare with all films in database

    :returns True if film with same title, rate,
    """
    new_title = film.film_title
    new_user_id = film.user_id
    new_date = film.release_date
    # TODO: add to check directors list also
    search = Films.query.filter_by(film_title=new_title,
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
        try:
            db.session.add(user)
        # this is test error handling, will catch different errors during dev process.
        except Exception as e:
            print(e)
            db.session.rollback()
        else:
            db.session.commit()
    else:
        raise ValueError("User with same email already registered")


def add_director(full_name: str):
    """ Add film's director row in database

    :param full_name: string name

    :returns None
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


def add_film(film_title: str, release_data: datetime, user: int or User,
             director_name: str, genres: list, film_description: str = None,
             film_rate: int = 0, poster_url: str = "https://"):
    """ Create film row in database and add row to Films table in db.

    :param film_title: string film name

    :param release_data: datetime type release time. As example, datetime.datetime(1996, 1, 19)

    :param user: unique integer id of user who added film. Also can be User instance

    :param director_name: str name, goes to directors table

    :param film_description string, default is None

    :param film_rate integer from 0 to 10 including, default is 10.

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

    film = Films(film_title=film_title, film_description=film_description,
                 user_id=int(user_id), film_rate=film_rate, release_date=release_data, poster_url=poster_url)

    if validate_film(film) is not True:
        try:
            # trying to add new film to db table
            db.session.add(film)
            print(f"Adding film {film.film_title}")
        # this is test error handling, will catch different errors during dev process.
        except Exception as e:
            print(e)
            print(f"Error adding film {film.film_title}")
            db.session.rollback()
        else:
            # if films inserted successfully, inserting everything else
            # making record to directors table
            add_director(full_name=director_name)
            # record to relation directors-films
            director = Directors.query.filter_by(full_name=director_name).first()
            director.films.append(film)
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
            db.session.commit()
    else:
        raise TypeError(f"Film {film.film_title} already added.")
