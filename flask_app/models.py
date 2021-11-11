""" Database models module made with flask-SQLAlchemy
 Notices:
 - no need to make column autoincrement=True if it is 1st integer column with no foreign key.
 """
import json
from datetime import datetime

from .app import db
from flask import jsonify, g

# Many To Many relationship between users and uploaded films
users_films = db.Table('usersfilms',
                       db.Column('user_id', db.ForeignKey('users.id'), primary_key=True),
                       db.Column('film_id', db.ForeignKey('films.id'), primary_key=True)
                       )

# Many To Many relationship between directors and films
films_directors = db.Table('filmsdirectors',
                           db.Column('director_id', db.Integer, db.ForeignKey('directors.id')),
                           db.Column('film_id', db.Integer, db.ForeignKey('films.id'))
                           )

# Many To Many relationship between films and genres
films_genres = db.Table('filmsgenres',
                        db.Column('films_id', db.ForeignKey('films.id'), primary_key=True),
                        db.Column('genres_id', db.ForeignKey('genres.id'), primary_key=True)
                        )


class User(db.Model):
    """ Model for user table. """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nickname = db.Column(db.String(20), default='guest')
    email = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(), nullable=False)
    country = db.Column(db.String)
    city = db.Column(db.String)
    street = db.Column(db.String)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """ Magic method for useful printing info about instance """
        return f"User with id: {self.id}. Full: {self.__dict__}"


class Films(db.Model):
    """ Model for films table.

    :param film_title: string film's name

    :param film_description: string full film's description

    :param film_rate: int rate number 0-10 (including)

    :param release_date: timestamp release date. For example datetime.datetime(2018, 09, 12)

    :param poster_link: string with poster img url.

    """
    __tablename__ = 'films'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    film_title = db.Column(db.String, nullable=False)
    film_description = db.Column(db.String)
    film_rate = db.Column(db.Integer, default=0)
    release_date = db.Column(db.TIMESTAMP)
    poster_url = db.Column(db.String)
    user_id = db.Column(db.Integer)

    # Many-to-many relation with table users_films
    # 'films' in backrefs is the name of "column" id User class.
    # for adding films by append to instance(user.films.append(film))
    users = db.relationship("User", secondary=users_films, backref=db.backref("films", lazy="dynamic"))
    # Many-to-many relation with table directors
    directors = db.relationship("Directors", secondary=films_directors, backref=db.backref("films", lazy="dynamic"))
    genres = db.relationship("Genres", secondary=films_genres, backref=db.backref("films", lazy="dynamic"))

    def to_dict(self):
        """ Create dict from attributes to adopt it for json. """
        data = dict(id=self.id, film_title=self.film_title, film_description=self.film_description,
                    film_rate=self.film_rate, release_date=datetime.strftime(self.release_date, "%Y.%m.%d"),
                    poster_url=self.poster_url, user_id=self.user_id)
        return data


class Directors(db.Model):
    """ Model for director table.

    :param full_name: string name

    :returns None
    """
    __tablename__ = 'directors'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    full_name = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        """ Magic method for useful printing info about instance """
        return f"Director with id: {self.id}"


class Genres(db.Model):
    """ Model for genre table.

        :param name: string genre name

    """
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        """ Magic method for useful printing info about instance """
        return f"Genre {self.name} with id: {self.id}"


db.create_all()
