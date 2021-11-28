""" Main entry point. Useful for local launches. """
from films_library import films_app
# need import resourced api version instead of empty in films_library/__init__.py
from films_library.api import films_api


# check if all routes added
print(films_app.url_map)

if __name__ == "__main__":
    # there is should be adding default director "unknown"
    # but it brokes migrations so this one-time action was moved to app's docker-file
    films_app.run()
