""" Main entry point. Useful for local launches. """
from films_library import films_app
# need import resourced api version instead of empty in films_library/__init__.py
from films_library.api import films_api
from films_library.logger import Log


# check if all routes added
print(films_app.url_map)

if __name__ == "__main__":
    # there is should be adding default director "unknown"
    # but it breaks migrations so this one-time action was moved to app's docker-file
    Log.info("Starting application...")
    films_app.run()
