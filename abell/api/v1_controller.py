from functools import wraps
from flask import request, Response, jsonify, g, session

from ..api import api, internal
from abell.database import AbellDb
from abell.models import AbellAsset
from responses import abell_error, abell_success

import json

ABELLDB = AbellDb()

FLAGS = {'create_keys': {'action': ['create'],
                         'auth': ['admin']}}


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
    response_dict = {'success': False,
                     'error': None}
    for field in fields:
        if field not in data:
            response_dict['error'] = abell_error(400,
                                                 '%s payload does not contain '
                                                 'required fields %s'
                                                 % (action, str(fields)))

    response_dict.update({'success': True})
    return response_dict


def update_asset_type(data_keys, abell_asset_info):
    response_dict = {'success': True,
                     'error': None,
                     'message': None}
    asset_type = abell_asset_info.get('type')
    given_keys = set(data_keys)
    validate_keys = set(['owner', 'cloud', 'type', 'abell_id'])
    potential_keys = given_keys.difference(validate_keys)
    existing_keys = set(abell_asset_info.get('managed_keys') +
                        abell_asset_info.get('unmanaged_keys'))

    # TODO(mike) check if system keys (may need to rethink)
    new_keys = potential_keys.difference(existing_keys)
    if new_keys:
        ABELLDB.update_managed_vars(asset_type, list(new_keys))
        db_resp = ABELLDB.add_new_key(asset_type, list(new_keys))
        return db_resp
    return response_dict


def create_new_asset(asset_type, asset_data, asset_info=False):
    # TODO(mike) Grab asset info if none
    abell_id = asset_data.get('abell_id')
    new_asset = AbellAsset(asset_type, asset_info, abell_id)
    new_asset.create_asset(asset_data)
    payload = new_asset.stringified_attributes()
    db_response = ABELLDB.add_new_asset(payload)
    return db_response


@api.route('/v1/create', methods=['POST'])
@validate_json
# todo auth
def create_one_asset():
    # Check if new keys are to be added to data type
    data = dict(request.get_json())
    flags = dict(request.args)
    response_details = {}

    # Ensure Data has required options
    validate_response = validate_data('create', data,
                                      ['owner', 'cloud', 'type', 'abell_id'])
    if not validate_response.get('success'):
        return validate_response.get('error')

    # Ensure asset type exists
    given_asset_type = data.get('type')
    abell_asset_info = ABELLDB.get_asset_info(given_asset_type)
    if not abell_asset_info:
        response_details.update({'submitted_data': data})
        return abell_error(400,
                           '%s asset type does not exist. Check submitted '
                           'type or have an admin create it'
                           % given_asset_type,
                           **response_details)

    # Create new keys if create_keys flag is set
    if request.args.get('create_keys', 'false').lower() == 'true':
        new_key_resp = update_asset_type(data.keys(), abell_asset_info)
        if not new_key_resp.get('success'):
            return abell_error(new_key_resp.get('error'),
                               new_key_resp.get('message'))
        new_keys_added = new_key_resp.get('message')
        response_details.update({'new_keys_added': new_keys_added})
        abell_asset_info = ABELLDB.get_asset_info(given_asset_type)

    # Create new asset
    db_status = create_new_asset(given_asset_type, data, abell_asset_info)
    if not db_status.get('success'):
        return abell_error(db_status.get('error'),
                           db_status.get('message'),
                           **response_details)
    else:
        response_details.update({'info': db_status.get('message')})
        return abell_success(**response_details)

    return abell_error(500,
                       'Unknown create error',
                       submission=data)
