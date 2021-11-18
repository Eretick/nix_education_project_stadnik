""" Database models module made with flask-SQLAlchemy
 Notices:
 - no need to make column autoincrement=True if it is 1st integer column with no foreign key.
 """
import json
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from flask_app.app import db
from flask import jsonify
from flask_login import UserMixin

# Many To Many relationship between users and uploaded films
users_films = db.Table('usersfilms',
                       db.Column('film_id', db.ForeignKey('films.id')),
                       db.Column('user_id', db.ForeignKey('users.id'))
                       )

# Many To Many relationship between directors and films
films_directors = db.Table('filmsdirectors',
                           db.Column('film_id', db.Integer, db.ForeignKey('films.id')),
                           db.Column('director_id', db.Integer, db.ForeignKey('directors.id')),
                           )

# Many To Many relationship between films and genres
films_genres = db.Table('filmsgenres',
                        db.Column('film_id', db.ForeignKey('films.id')),
                        db.Column('genres_id', db.ForeignKey('genres.id'))
                        )


class User(UserMixin, db.Model):
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

    def __init__(self, **kwargs):
        if "password" in kwargs:
            self.set_password(kwargs["password"])
        if "nickname" in kwargs:
            self.set_nickname(kwargs["nickname"])
        if "email" in kwargs:
            self.set_email(kwargs["email"])
        if "country" in kwargs:
            self.set_country(kwargs["country"])
        if "street" in kwargs:
            self.set_street(kwargs["street"])
        if "city" in kwargs:
            self.set_city(kwargs["city"])
        if "is_admin" in kwargs:
            self.set_admin(kwargs["is_admin"])

    def __repr__(self):
        """ Magic method for useful printing info about instance """
        return f"User with id: {self.id}. Full: {self.__dict__}"

    def to_dict(self):
        """ Create dict from attributes to adopt it for json. """
        data = dict(id=self.id, nickname=self.nickname, email=self.email,
                    password=self.password, country=self.country,
                    city=self.city, street=self.street, is_admin=self.is_admin)
        return data

    def set_password(self, new_password: str):
        """ Set hash password version for hide real password.
        :param new_password: original password user entered.

        :returns None
        """
        self.password = generate_password_hash(new_password)

    def check_password(self, password: str):
        """ Check if user has passed password value.
            :param password: original password user entered.

            :returns None
            """
        return check_password_hash(self.password, password)

    def set_nickname(self, new_name: str):
        """ Method for change/set user's nickname """
        self.nickname = new_name

    def set_email(self, new_email: str):
        """ Simple variation of user's email changing. """
        self.email = new_email

    def set_country(self, new_country: str):
        """ Method for user's country changing. """
        self.country = new_country

    def set_city(self, new_city: str):
        """ Method for user's city changing """
        self.city = new_city

    def set_street(self, new_street: str):
        """ Method for changin user's street. """
        self.street = new_street

    def set_admin(self, mode: bool):
        """ Method for changin user's admin mode. """
        self.is_admin = mode


class Films(db.Model):
    """ Model for films table.

    :param title: string film's name

    :param description: string full film's description

    :param rate: int rate number 0-10 (including)

    :param release_date: timestamp release date. For example datetime.datetime(2018, 09, 12)

    :param poster_link: string with poster img url.

    """
    __tablename__ = 'films'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    rate = db.Column(db.Float, default=0)
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
        data = dict(id=self.id, title=self.title, description=self.description,
                    rate=self.rate, release_date=datetime.strftime(self.release_date, "%Y.%m.%d"),
                    poster_url=self.poster_url, user_id=self.user_id)
        return data

    def set_title(self, title: str):
        """ Method for changing film's title """
        if title != self.title:
            if isinstance(title, str):
                self.title = title
            else:
                if title is not None:
                    raise TypeError("Wrong title type!")

    def set_description(self, description: str):
        """ Method for changing film's description """
        if description != self.description:
            if isinstance(description, str):
                self.description = description
            else:
                if description is not None:
                    raise TypeError("Wrong description type!")

    def set_rate(self, rate: int):
        """ Method for changing film's rate """
        if isinstance(rate, int) and rate != self.rate:
            self.rate = rate
        else:
            if rate is not None:
                raise TypeError("Wrong rate type!")

    def set_release_date(self, release_date: str):
        """ Method for changing film's release_date """

        if release_date is not None:
            if release_date != self.release_date:
                self.release_date = datetime.strptime(release_date, "%Y.%m.%d")
            else:
                raise TypeError("Wrong date type!")

    def set_poster_url(self, poster_url: str):
        """ Method for changing film's poster_url """
        if isinstance(poster_url, str):
            if poster_url != self.poster_url:
                self.poster_url = poster_url
            else:
                raise TypeError("Wrong poster type!")

    def set_user_id(self, user_id: int):
        """ Method for changing film's user_id """
        if user_id != self.user_id:
            self.user_id = user_id
        else:
            if user_id is not None:
                raise TypeError("Wrong user_id type!")


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
