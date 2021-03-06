""" Custom errors """


class BadRequestError(Exception):
    """ Error class for 401 (bad request) http status code """
    status_code = 400
    message = "Bad request"

    def __init__(self, message=None, status_code=None, payload=None):
        if self.message is not None:
            self.message = message
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        super().__init__(self, message)

    def to_dict(self):
        """ Method for response serialization """
        data = dict(self.payload or ())
        data["message"] = self.message
        return data


class NotAuthenticatedError(BadRequestError):
    """ Error class for 401 (unauthorized) http status code """
    status_code = 401
    message = "Action denied for unauthorized users!"


class NotFoundError(BadRequestError):
    """ Error class for 404 (not found) http status code """
    status_code = 404
    message = "Not found"


class UserPermissionError(BadRequestError):
    """ Error class for 403 (forbidden) error in case of user permission. """
    status_code = 403
    message = "You don't have rights for this action."


class GeneralForbiddenError(BadRequestError):
    """ Error class for 403 (forbidden) error in general case. """
    status_code = 403
    message = "Action denied."
