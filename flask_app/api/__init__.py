from flask_app import models
from flask_app.app import login_manager


@login_manager.user_loader
def load_user(id):
    """ For keeping user in session """
    return models.User.query.get(int(id))




