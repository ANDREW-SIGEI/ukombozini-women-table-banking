from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response

def bad_request(message):
    return error_response(400, message)

class ValidationError(Exception):
    pass

class ResourceNotFoundError(Exception):
    pass

class AuthorizationError(Exception):
    pass

def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def validation_error(e):
        return bad_request(str(e))

    @app.errorhandler(404)
    def not_found_error(e):
        return error_response(404)

    @app.errorhandler(ResourceNotFoundError)
    def resource_not_found_error(e):
        return error_response(404, str(e))

    @app.errorhandler(AuthorizationError)
    def authorization_error(e):
        return error_response(403, str(e))

    @app.errorhandler(500)
    def internal_error(e):
        return error_response(500, 'An unexpected error has occurred')

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response(405, 'The method is not allowed for the requested URL') 