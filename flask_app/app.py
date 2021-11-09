# is not null in query.filter(User.name.isnot(None))
import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# create and setup app
app = Flask(__name__)
app.config.from_mapping(SECRET_KEY=os.environ.get('SECRET_KEY', default='dev'),
                        SQLALCHEMY_TRACK_MODIFICATIONS=False,
                        SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI',
                                                               default='sqlite:///db.db'),
                        DEBUG=True)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# importing from top of file makes circular imports
from flask_app import routes, models
#print(models.User.query.all())

# launch app
app.run()
