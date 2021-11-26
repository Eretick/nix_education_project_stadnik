""" Main entry point. Useful for local launches. """
from films_library import films_app, db
# need import resourced api version instead of empty in films_library/__init__.py
from films_library.api import films_api
from films_library.database import add_director


# check if all routes added
print(films_app.url_map)

if __name__ == "__main__":
    # adding default Director value for non bound directors
    # after everything  was initialized
    #films_app.db.create_all()
    add_director("unknown")
    films_app.run()
