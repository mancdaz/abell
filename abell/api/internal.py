from functools import wraps
from flask import request
from errors import *
from abell.database import AbellDb

import errors
import json

ABELLDB = AbellDb()


def validate_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            request.get_json()
        except:
            error_response = abell_error(400, 'JSON formatting error')
            return error_response
        return f(*args, **kwargs)
    return decorated_function


def validate_data(action, data, fields):
    response_dict = {'success': True,
                     'error': None}
    for field in fields:
        if field not in data:
            response_dict['success'] = False
            response_dict['error'] = abell_error(400,
                                                 '%s payload does not contain '
                                                 'required fields %s'
                                                 % (action, str(fields)))

    return response_dict


# def build_asset(data):
#     validate_response = validate_data(data, ['owner', 'cloud', 'type',
#                                              'abell_id'])
#     if not validate_response.get('success'):

@validate_json
def create_asset():
    flags = dict(request.args)
    create_keys = False
    if request.args.get('create_keys').lower() == 'true':
        create_keys = True
    data = dict(request.get_json())
    validate_response = validate_data('create', data,
                                      ['owner', 'cloud', 'type', 'abell_id'])
    # Ensure Data has required options
    if not validate_response.get('success'):
        return validate_response.get('error')

    asset_type = data.get('type')
    asset_type_info = ABELLDB.get_asset_type(asset_type=asset_type)
    if not asset_type_info:
        return abell_error(400,
                           '%s asset type does not exist. Check submitted '
                           'type or have an admin create it' % asset_type,
                           submission=data)
    # print create_keys
    return '%s' % asset_type_info
