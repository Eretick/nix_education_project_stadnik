import pytest
# importing modules completely for making app see his api routes
from flask_app.app import films_app
from flask_app.models import User, Films, Directors
from flask_app.api.films_api import load_user  # flask need it

# Urls
BASE_URL = "/api/"
FILMS_URL = BASE_URL + "films/"
USERS_URL = BASE_URL + "users/"
LOGIN_URL = USERS_URL + "login/"
LOGOUT_URL = USERS_URL + "logout/"
PROFILE_URL = USERS_URL + "profile/"
DIRECTORS_URL = BASE_URL + "directors/"

USER1_DATA = {"email": "user1@mail.ua", "password": "pass1"}
FILM_DATA = {"title": "Film1", "description": "desc1", "directors": "director1,director2",
             "rate": 5, "date": "2010.02.01", "poster_url": "https:/img.png", "genres": "Action,Noir"}
DIRECTOR_NAME = "Sten Lee"
DIRECTOR_NAME_UNEXISTS = "sfsdf dskf ksdh fskfsdk fsk fasklds"


@pytest.fixture
def client():
    """ fixture for testing application """
    with films_app.test_client() as client:
        yield client


@pytest.fixture
def login_user(client):
    user = client.post(LOGIN_URL, data=USER1_DATA)
    return user


def test_index(client):
    """ Test if app can get main page """
    response = client.get(BASE_URL)
    assert response.status_code == 200


def test_login(client):
    """ Test for login function with given email and password from non_empty database """
    users = User.query.all()
    assert len(users) != 0, "Database has no users records in Users table!"
    response = client.post(LOGIN_URL, data=USER1_DATA)
    assert response.status_code == 200, "Login error. Check UserLogin post method."


def test_unauthorized_profile(client):
    """ Check unauthorized status while try to open profile without login """
    response = client.get(PROFILE_URL)
    assert response.status_code == 401


def test_authorized_profile(client, login_user):
    """ Check open profile after login """
    assert login_user.status_code == 200
    response = client.get(PROFILE_URL)
    assert response.status_code == 200
    assert login_user.json["users"]["email"] == USER1_DATA["email"]


def test_logout(client, login_user):
    """ Test of logout feature """
    logout = client.get(LOGOUT_URL)
    # check if logout successfull
    assert logout.status_code == 200
    # check if logged in and logged out users are the same account
    assert logout.json == login_user.json["users"]["nickname"]
    # check if now not authorized
    response = client.get(PROFILE_URL)
    assert response.status_code == 401


def test_get_films(client):
    """ Simple films get test. Returns status code 200 if (any) films was found.  """
    response = client.get(FILMS_URL)
    assert response.status_code == 200


def test_add_film_unauthorized(client):
    """ Check add film without login """
    new_film = client.post(FILMS_URL, data=FILM_DATA)
    assert new_film.status_code == 401


def test_add_film_authorized(client, login_user):
    """ Check add film by user feature """
    new_film = client.post(FILMS_URL, data=FILM_DATA)
    # if film wasn't added earlier
    if new_film.status_code != 403:
        # success if film was added (got 201)
        assert new_film.status_code == 201


def test_find_by_template(client, login_user):
    """ Check if recently added film is in db """
    assert Films.query.filter_by(title=FILM_DATA["title"]).first() is not None


def test_delete_film(client, login_user):
    """ Check delete feature """
    id = Films.query.filter_by(title=FILM_DATA["title"]).first().id
    deleted = client.delete(FILMS_URL, data={"id": id})
    assert deleted.status_code == 200
    assert Films.query.filter_by(title=FILM_DATA["title"]).first() is None


def test_add_director(client, login_user):
    """ Adding director to Directors database table """
    # check database doesn't have this director
    if Directors.query.filter_by(full_name=DIRECTOR_NAME).first() is None:
        new = client.post(DIRECTORS_URL, data={"director_name": DIRECTOR_NAME})
        assert new.status_code == 201
    else:
        assert 200, f"Director {DIRECTOR_NAME} is already added"


def test_delete_not_exists_director(client, login_user):
    """ Trying delete director if he not in database """
    # check database doesn't have this director
    assert Directors.query.filter_by(full_name=DIRECTOR_NAME_UNEXISTS).first() is None, "You must specify not existed director's name!"
    new = client.delete(DIRECTORS_URL, data={"director_name": DIRECTOR_NAME_UNEXISTS})
    assert new.status_code == 403


def test_delete_director(client, login_user):
    """ Adding director to Directors database table """
    # check database doesn't have this director
    assert Directors.query.filter_by(full_name=DIRECTOR_NAME).first() is not None, "You must specify existed director's name!"
    new = client.delete(DIRECTORS_URL, data={"director_name": DIRECTOR_NAME})
    assert new.status_code == 200
