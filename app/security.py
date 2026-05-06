from functools import wraps

from flask import jsonify, request

from app.config import API_KEY


def require_api_key(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        provided_key = request.headers.get("X-API-Key")

        if provided_key != API_KEY:
            return jsonify({
                "error": "Unauthorized. Missing or invalid API key."
            }), 401

        return route_function(*args, **kwargs)

    return wrapper