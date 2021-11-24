""" Module for generating some fake data """
import datetime
from flask_app.database import add_film, add_user, add_genre
import csv


def read_csv(file):
    """ func for read data from csv file """
    films_data = []
    with open(file, encoding="utf8") as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            films_data.append(row)
    return films_data


def fill_films_and_directors(films_list: list):
    """ Func to fill db with fake films and directors """
    for row in films_list:
        add_film(title=row[0], release_date=datetime.datetime.strptime(row[4], "%Y.%m.%d"),
                 user=row[6], directors=row[2], genres=row[7], description=row[1],
                 rate=row[3], poster_url=row[5])


def fill_users(users_list: list):
    """ Func to fill db with fake users """
    for row in users_list:
        add_user(nickname=row[0], email=row[1], password=row[2], country=row[3],
                 city=row[4], street=row[5], is_admin=bool(row[6]))


def fill_genres(genres_list: list):
    """ Func to fill db with fake genres """
    for row in genres_list:
        add_genre(genre_name=row[0])


def fill_db():
    print("Generating fake data...")
    users = read_csv("users.csv")
    films = read_csv("films.csv")
    genres = read_csv("genres.csv")
    # users first
    fill_users(users)
    # then genres (doesn't matter)
    fill_genres(genres)
    # then (the last one!) films
    fill_films_and_directors(films)


if __name__ == "__main__":
    fill_db()