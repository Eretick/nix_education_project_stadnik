# set app as flask default app
set_flask_app:
    export FLASK_APP=flask_app/app.py

# creating db migration
db_init:
    flask db init
    flask db migrate

# upgrading bd after changes
db_upgrade:
    flask db migrate
    flask db upgrade

# downgrading bd
db_downgrade:
    flask db downgrade