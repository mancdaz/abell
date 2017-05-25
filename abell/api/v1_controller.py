from functools import wraps
from flask import request
from ..api import api
from abell.models import asset
from .responses import abell_error, abell_success

# import json

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
            return response_dict
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
        for k, v in request_args.items():
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
        db_result = asset.asset_find(asset_type,
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
        db_result = asset.asset_count(asset_type,
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
def distinct_fields():
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
        db_result = asset.distinct_asset_fields(asset_type,
                                                      params,
                                                      distinct_key)
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


@api.route('/v1/update', methods=['PUT'])
@validate_json
# todo auth
def update_assets():
    data = dict(request.get_json())
    update_multiple = False
    validate_response = validate_data('update', data, ['update', 'filter'])
    if not validate_response.get('success'):
        return validate_response.get('error')
    # Get multi update flag AUTH AUTH AUHT
    if request.args.get('update_multiple_assets', 'false').lower():
        update_multiple = True
    asset_filter = data.get('filter')
    asset_update = data.get('update')
    asset_type = asset_filter.get('type')
    # TODO(mike) Figure out Cache for allowed asset types
    # if object_type is not None and object_type not in ALLOWED_COLLECTIONS:
    # error_response = galaxy_error(404,
    #   'Asset type is not found',
    #   type=object_type)
    # return error_response
    if update_multiple:
        test = asset.update_asset_values(asset_type,
                                               asset_filter,
                                               asset_update,
                                               auth_level='admin',
                                               multi=update_multiple)
        #update many


    return abell_success(**data)


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
    abell_asset_info = asset.get_asset_type(given_asset_type)
    if not abell_asset_info:
        response_details.update({'submitted_data': data})
        return abell_error(400,
                           '%s asset type does not exist. Check submitted '
                           'type or have an admin create it'
                           % given_asset_type,
                           **response_details)

    # Create new keys if create_keys flag is set
    if request.args.get('create_keys', 'false').lower() == 'true':
        new_key_resp = asset.update_asset_type(data.keys(),
                                                     abell_asset_info)
        if not new_key_resp.get('success'):
            return abell_error(new_key_resp.get('error'),
                               new_key_resp.get('message'))
        new_keys_added = new_key_resp.get('message')
        response_details.update({'new_keys_added': new_keys_added})
        abell_asset_info = asset.get_asset_type(given_asset_type)

    # Create new asset
    db_status = asset.create_new_asset(given_asset_type,
                                             data, abell_asset_info)
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
