""" Database models module made with flask-SQLAlchemy
 Notices:
 - no need to make column autoincrement=True if it is 1st integer column with no foreign key.
 """
from app import db

# Many To Many relationship between users and uploaded films
users_films = db.Table('usersfilms',
                       db.Column('user_id', db.ForeignKey('users.id'), primary_key=True),
                       db.Column('film_id', db.ForeignKey('films.id'), primary_key=True)
                       )

# Many To Many relationship between directors and films
films_directors = db.Table('filmsdirectors',
                       db.Column('director_id', db.ForeignKey('directors.id'), primary_key=True),
                       db.Column('film_id', db.ForeignKey('films.id'), primary_key=True)
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
    country = db.Column(db.String)
    city = db.Column(db.String)
    street = db.Column(db.String)
    registered = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    # somehow raise an error with query models.User.query.all()
    # Many-to-many relation with table users_films
    # users_films = db.relationship('Film', secondary=users_films, lazy='subquery',
    #                               back_populates=db.backref('users', lazy=True))

    def __repr__(self):
        """ Magic method for useful printing info about instance """
        return f"User with id: {self.id}"


class Film(db.Model):
    """ Model for films table. """
    __tablename__ = 'films'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    film_title = db.Column(db.String, nullable=False)
    film_description = db.Column(db.String)
    film_rate = db.Column(db.Integer, default=0)
    release_date = db.Column(db.TIMESTAMP)
    poster_link = db.Column(db.String, unique=True)
    # Many-to-many relation with table users_films
    # somehow raise an error with query models.User.query.all()
    # users_films = db.relationship('User', secondary=users_films, lazy='subquery',
    #                               back_populates=db.backref('films', lazy=True))


    def __repr__(self):
        """ Magic method for useful printing info about instance """
        return f"Film with id: {self.id}"


class Directors(db.Model):
    """ Model for director table. """
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    second_name = db.Column(db.String, nullable=False)

    def __repr__(self):
        """ Magic method for useful printing info about instance """
        return f"Director with id: {self.id}"


class Genres(db.Model):
    """ Model for genre table. """
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        """ Magic method for useful printing info about instance """
        return f"Genre {self.name} with id: {self.id}"

db.create_all()  # uncomment for server version