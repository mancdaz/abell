from functools import wraps
from flask import request
from ..api import api
from abell.database import AbellDb
from abell.models import AbellAsset
from responses import abell_error, abell_success

# import json

ABELLDB = AbellDb()

FLAGS = {'create_keys': {'action': ['create'],
                         'auth': ['admin']}}


def validate_json(f):
    """Validate json input.

    Attempts to extract JSON from user request.
    Args:
        Request function (wrapped)
    Returns:
        Abell error if JSON is not formatted correctly
    """
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
    """General Field Validator

    Ensures the required fields for a certain action are provided by the user.
    Args:
        action (str): Action the user is attempting
        data (dict): User provided data
        fields (list): List of required fields
    Returns:
        Response dict: {'success': bool, 'error': None | abell_error}
    """
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


def get_query_params(request_args):
    response_dict = {'success': False,
                     'error': None,
                     'params': None,
                     'specified_keys': None,
                     'distinct_key': None}
    params = dict()
    specified_keys = {'_id': 0}
    try:
        for k, v in request_args.iteritems():
            if k == 'distinct_key':
                response_dict['distinct_key'] = v
            elif k == 'specified_keys':
                keys = v.replace('[', '').replace(']', '').split(',')
                for key in keys:
                    specified_keys.update({key.strip(): 1})
            elif v[0] == '!':
                params[k.lower()] = {'$ne': v[1:]}
            elif v[0] == '/':
                params[k.lower()] = {'$regex': v[1:]}
            else:
                params[k.lower()] = v

        response_dict.update({'success': True, 'params': params,
                             'specified_keys': specified_keys})
        return response_dict

    except Exception:
        error_response = abell_error(400,
                                     'Error in filter params')
        response_dict['error'] = error_response
        return response_dict


def update_asset_type(data_keys, abell_asset_info):
    """Add new fields to an asset type

    Adds new fields to an abell asset type.
    Args:
        data_keys (list): List of user provided keys for updating
        abell_asset_info (dict): Abell asset information dict
    Returns:
        Response dict: {'success': bool, 'error': None | abell_error}
    """
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
    """Create a new asset in abell

    Args:
        asset_type (str): abell asset type
        asset_data (dict): user provided asset data
        asset_info (dict): Abell asset information dict
    Returns:
        Response dict: Database response dict
    """
    # TODO(mike) Grab asset info if none
    abell_id = asset_data.get('abell_id')
    new_asset = AbellAsset(asset_type, asset_info, abell_id)
    new_asset.create_asset(asset_data)
    payload = new_asset.stringified_attributes()
    db_response = ABELLDB.add_new_asset(payload)
    return db_response


@api.route('/v1/find', methods=['GET'])
# todo auth
def find_assets():
    response_details = {}
    query_params = get_query_params(request.args)

    if not query_params.get('success'):
        return query_params['error']
    else:
        params = query_params.get('params')
        specified_keys = query_params.get('specified_keys')
        response_details.update({'query_params': params})

    asset_type = params.get('type')
    # TODO(mike) Figure out Cache for allowed asset types
    # if object_type is not None and object_type not in ALLOWED_COLLECTIONS:
    # error_response = galaxy_error(404,
    #   'Asset type is not found',
    #   type=object_type)
    # return error_response
    if asset_type:
        db_result = ABELLDB.asset_find(asset_type,
                                       params,
                                       specified_keys=specified_keys)
        if not db_result.get('success'):
            # DB Error
            return abell_error(db_result.get('error'),
                               db_result.get('message'),
                               **response_details)
        else:
            # Successful find!
            payload = list(db_result.get('result'))
            return abell_success(payload=payload,
                                 **response_details)

    return abell_error(500,
                       'Unknown find error',
                       submission=query_params)


@api.route('/v1/count', methods=['GET'])
# todo auth
def count_assets():
    response_details = {}
    query_params = get_query_params(request.args)
    if not query_params.get('success'):
        return query_params['error']
    else:
        params = query_params.get('params')
        response_details.update({'query_params': params})
    asset_type = params.get('type')
    # TODO(mike) Figure out Cache for allowed asset types
    # if object_type is not None and object_type not in ALLOWED_COLLECTIONS:
    # error_response = galaxy_error(404,
    #   'Asset type is not found',
    #   type=object_type)
    # return error_response
    if asset_type:
        db_result = ABELLDB.asset_count(asset_type,
                                        params)
        if not db_result.get('success'):
            # DB Error
            return abell_error(db_result.get('error'),
                               db_result.get('message'),
                               **response_details)
        else:
            # Successful count!
            payload = {'count': db_result.get('result')}
            return abell_success(payload=payload,
                                 **response_details)

    return abell_error(500,
                       'Unknown count error',
                       submission=query_params)


@api.route('/v1/distinct', methods=['GET'])
# todo auth
def distinct_assets():
    response_details = {}
    query_params = get_query_params(request.args)
    if not query_params.get('success'):
        return query_params['error']
    else:
        params = query_params.get('params')
        distinct_key = query_params.get('distinct_key')
        response_details.update({'query_params': params,
                                 'distinct_key': distinct_key})
    asset_type = params.get('type')
    # TODO(mike) Figure out Cache for allowed asset types
    # if object_type is not None and object_type not in ALLOWED_COLLECTIONS:
    # error_response = galaxy_error(404,
    #   'Asset type is not found',
    #   type=object_type)
    # return error_response
    if asset_type:
        db_result = ABELLDB.asset_distinct(asset_type,
                                           params,
                                           str(distinct_key))
        if not db_result.get('success'):
            # DB Error
            return abell_error(db_result.get('error'),
                               db_result.get('message'),
                               **response_details)
        else:
            # Successful distinct call!
            payload = db_result.get('result')
            return abell_success(payload=payload,
                                 **response_details)

    return abell_error(500,
                       'Unknown distinct error',
                       submission=query_params)


@api.route('/v1/create', methods=['POST'])
@validate_json
# todo auth
def create_one_asset():
    # Check if new keys are to be added to data type
    data = dict(request.get_json())
    # flags = dict(request.args)
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
