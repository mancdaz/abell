from functools import wraps
from flask import request
from ..api import api
from abell.models import asset_type as AT
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


@api.route('/v1/asset_type', methods=['POST'])
@validate_json
def create_asset_type():
    """Create new asset type

    Handles the creation of a new asset type. Creates a new entry in the
    assetinfo collection, as well as creating the collection for the actual
    assets of the given type.
    Args:
        Takes a json formatted dict from the post which must contain the new
        data type.
        EX:{'type': 'server',
            'managed_keys': [key1,key2],
            'unmanaged_keys':[key3,key4]}
    Returns:
        Response dict: {'code': int, 'payload': null}
    """
    data = dict(request.get_json())
    response_details = {}
    valid_data = validate_data('create', data, ['type'])

    if not valid_data.get('success'):
        return valid_data.get('error')

    new_asset_type = data.get('type')
    managed_keys = data.get('managed_keys', [])
    unmanaged_keys = data.get('unmanaged_keys', [])
    if type(managed_keys) is not list or type(unmanaged_keys) is not list:
        return abell_error(400,
                           'managed_keys and unmanaged_keys must by lists')
    new_asset_info = {'managed_keys': managed_keys,
                      'unmanaged_keys': unmanaged_keys}

    new_asset = AT.AbellAssetType(new_asset_type,
                                  asset_info=new_asset_info)
    result = new_asset.create_new_type()
    if result.get('success'):
        response_details.update(
            {'info': 'Asset type %s created' % new_asset_type})
        return abell_success(**response_details)
    return abell_error(400, result.get('message', 'Asset type create error'))


@api.route('/v1/asset_type', methods=['GET'])
# todo auth
def return_asset_info():
    """Get asset info

    Returns asset type information
    Args:
        takes type from arguments
        EX: GET .../v1/asset_type?type=server
    Returns:
        Response dict: {'code': int, 'payload': dict, 'details': dict}
    """
    validate_response = validate_data('asset_info', request.args,
                                      ['type'])
    if not validate_response.get('success'):
        return validate_response.get('error')
    asset_type = request.args.get('type')

    abell_asset_type = AT.get_asset_type(asset_type)
    if abell_asset_type:
        return abell_success(payload=abell_asset_type.key_dict())

    return abell_error(404,
                       '%s asset type not found' % asset_type)


@api.route('/v1/asset_type', methods=['PUT'])
# todo auth
def update_asset_type():
    """Update asset info

    Removes or adds keys to asset types. Also handles the mass update for new
    or removed keys for all assets of that type.
    Args:
        Takes a json formatted dict from the post which must contain the new
        data type.
        EX:{'type': 'server',
            'remove_keys': ['key5']
            'managed_keys': ['key1','key2'],
            'unmanaged_keys':['key3','key4']}
    Returns:
        Response dict: {'code': int, 'payload': null,
                        'details': {'new keys': [],
                                    'removed_keys': [],
                                    'info': str}}
    """
    data = dict(request.get_json())
    response_details = {}
    valid_data = validate_data('update', data, ['type'])
    if not valid_data.get('success'):
        return valid_data.get('error')

    asset_type = data.get('type')
    abell_asset_type = AT.get_asset_type(asset_type)
    if not abell_asset_type:
        return abell_error(404,
                           '%s asset type not found' % asset_type)

    remove_keys = data.get('remove_keys', [])
    managed_keys = data.get('managed_keys', [])
    unmanaged_keys = data.get('unmanaged_keys', [])
    if (type(managed_keys) is not list or
       type(unmanaged_keys) is not list or
       type(remove_keys) is not list):
        return abell_error(400,
                           'managed_keys, unmanaged_keys and remove_keys '
                           'must by lists')
    r = abell_asset_type.update_keys(remove_keys, managed_keys, unmanaged_keys)
    if r.get('success'):
        response_details.update({'info': 'Asset %s updated' % asset_type,
                                 'removed_keys': r.get('removed_keys'),
                                 'new_keys': r.get('new_keys')})
        return abell_success(**response_details)
    return abell_error(500,
                       r.get('message', 'Asset update error'))


@api.route('/v1/asset_type', methods=['DELETE'])
# todo auth
def delete_asset_type():
    """Delete asset info

    Deletes asset type from database. NOTE: All assets of that type must be
    removed from the db before deleting type.
    Args:
        takes type from arguments
        EX: DELETE .../v1/asset_type?type=server
    Returns:
        Response dict: {'code': int, 'payload': dict, 'details': dict}
    """
    response_details = {}
    validate_response = validate_data('asset_info', request.args,
                                      ['type'])
    if not validate_response.get('success'):
        return validate_response.get('error')
    asset_type = request.args.get('type')
    abell_asset_type = AT.get_asset_type(asset_type)
    if not abell_asset_type:
        return abell_error(404,
                           '%s asset type not found' % asset_type)
    r = abell_asset_type.remove_type()

    if r.get('success'):
        response_details.update({'info': 'Asset type %s deleted' % asset_type})
        return abell_success(**response_details)
    return abell_error(400,
                       r.get('message', 'Asset type delete error'))


@api.route('/v1/asset', methods=['GET'])
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
            payload = db_result.get('result')
            return abell_success(payload=payload,
                                 **response_details)

    return abell_error(500,
                       'Unknown find error',
                       submission=query_params)


@api.route('/v1/asset/count', methods=['GET'])
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


@api.route('/v1/asset/distinct', methods=['GET'])
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


@api.route('/v1/asset', methods=['PUT'])
@validate_json
# todo auth
def update_assets():
    data = dict(request.get_json())
    response_details = {}
    update_multiple = False
    upsert = False
    validate_response = validate_data('update', data, ['update', 'filter'])
    if not validate_response.get('success'):
        return validate_response.get('error')
    # Get multi update flag AUTH AUTH AUHT
    if request.args.get('update_multiple_assets', 'false').lower() == 'true':
        update_multiple = True
    if request.args.get('create_new_asset', 'false').lower() == 'true':
        upsert = True
        contains_sys_keys = validate_data('update', data.get('update'),
                                          ['owner', 'cloud',
                                           'type', 'abell_id'])
        if not contains_sys_keys.get('success'):
            return contains_sys_keys.get('error')
    if upsert and update_multiple:
        return abell_error(400,
                           'Unable to create multiple new assets')
    asset_filter = data.get('filter')
    asset_update = data.get('update')
    asset_type = asset_filter.get('type')
    response = asset.update_asset_values(asset_type,
                                         asset_filter,
                                         asset_update,
                                         auth_level='admin',
                                         multi=update_multiple,
                                         upsert=upsert)
    if response.get('success'):
        response_details.update({
            'updated_asset_ids': response.get('updated_asset_ids'),
            'message': response.get('message'),
            'new_assets': response.get('new_assets'),
            'updated_keys': response.get('updated_keys')})
        return abell_success(**response_details)

    return abell_error(response.get('error', 500),
                       response.get('message', 'Unknown update error.'),
                       **asset_filter)


@api.route('/v1/asset', methods=['DELETE'])
@validate_json
def delete_assets():
    data = dict(request.get_json())
    response_details = {}
    delete_multiple = False
    valid_data = validate_data('delete', data,
                               ['filter'])
    if not valid_data.get('success'):
        return valid_data.get('error')

    # Check if multidelete
    if request.args.get('multi_delete', 'false').lower() == 'true':
        delete_multiple = True
    asset_filter = data.get('filter')
    asset_type = asset_filter.get('type')
    if not asset_type:
        return abell_error(400,
                           'No asset type found in filter')
    asset_response = asset.delete_assets(asset_type,
                                         asset_filter,
                                         auth_level='admin',
                                         multi=delete_multiple)
    if asset_response.get('success'):
        response_details.update({
            'deleted_asset_ids': asset_response.get('deleted_asset_ids'),
            'message': asset_response.get('message')})
        return abell_success(**response_details)
    return abell_error(asset_response.get('error', 500),
                       asset_response.get('message', 'Unknown delete error.'),
                       **asset_filter)


@api.route('/v1/asset', methods=['POST'])
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
    abell_asset_type = AT.get_asset_type(given_asset_type)
    if not abell_asset_type:
        response_details.update({'submitted_data': data})
        return abell_error(400,
                           '%s asset type does not exist. Check submitted '
                           'type or have an admin create it'
                           % given_asset_type,
                           **response_details)

    # Create new keys if create_keys flag is set
    if request.args.get('create_keys', 'false').lower() == 'true':
        r = abell_asset_type.add_new_keys(data.keys())
        if not r.get('success'):
            return abell_error(r.get('error', 500),
                               r.get('message', 'Error in asset create'))
        new_keys = r.get('new_keys')
        response_details.update({'new_keys_added': list(new_keys)})

    # Create new asset
    new_asset = asset.AbellAsset(given_asset_type, data.get('abell_id'),
                                 data, abell_asset_type)
    r = new_asset.insert_asset()
    if r.get('success'):
        response_details.update({'info': r.get('message')})
        return abell_success(**response_details)

    return abell_error(r.get('error', 500),
                       r.get('message', 'Unknown create error'),
                       **response_details)
