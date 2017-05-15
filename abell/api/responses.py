import json
from flask import Response


def abell_success(*args, **kwargs):
    success = {"code": 200,
               "payload": args,
               "details": kwargs}
    response = Response(json.dumps(success),
                        status=200,
                        mimetype="application/json")
    return response


def abell_error(code, *args, **kwargs):
    if code == 400:
        return four_oh_oh(*args, **kwargs)
    if code == 401:
        return four_oh_one(*args, **kwargs)
    if code == 404:
        return four_oh_four(*args, **kwargs)
    if code == 500:
        return five_oh_oh(*args, **kwargs)

    return five_oh_oh('Internal server error')


# Error Handler for 400's, REQUEST errors.
def four_oh_oh(*args, **kwargs):
    error = {"code": 400,
             "type": "client request error",
             "message": args,
             "details": kwargs}

    return flask_error_response(error)


# 401's Unauthorized
def four_oh_one(*args, **kwargs):
    error = {"code": 401,
             "type": "unauthorized",
             "message": args,
             "details": kwargs}

    return flask_error_response(error)


# 404's Resources Not Found
def four_oh_four(*args, **kwargs):
    error = {"code": 404,
             "type": "resource not found",
             "message": args,
             "details": kwargs}

    return flask_error_response(error)


# 500 Internal Server error
def five_oh_oh(*args, **kwargs):
    error = {"code": 500,
             "type": "internal server error",
             "message": args,
             "details": kwargs}
    return flask_error_response(error)


def flask_error_response(error_dict):
    error_code = error_dict.get('code', 500)
    message = error_dict.get('message')
    response = Response(json.dumps(error_dict),
                        status=error_code,
                        mimetype="application/json")
    response.headers['Error-Message'] = message
    return response
