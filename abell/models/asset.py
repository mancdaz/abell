# from repoze.lru import lru_cache
from abell.models import model_tools
from abell.database import AbellDb
ABELLDB = AbellDb()


def get_asset_type(asset_type):
    # Need to cache this data!
    return ABELLDB.get_asset_info(asset_type)


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


def update_asset_values(asset_type, asset_filter, user_update_dict,
                        auth_level='user', multi=False):
    asset_type_info = get_asset_type(asset_type)
    response_dict = {'success': False,
                     'error': None,
                     'message': None,
                     'updated_keys': {},
                     'updated_asset_ids': []}
    # TEMP Auth check, this will Change
    if auth_level is 'admin':
        valid_keys = set(asset_type_info.get('managed_keys') +
                         asset_type_info.get('unmanaged_keys'))
        for k, v in user_update_dict.items():
            if k.split('.')[0] in valid_keys:
                response_dict['updated_keys'][k] = v
    else:
        valid_keys = set(asset_type_info.get('unmanaged_keys'))
        for k, v in user_update_dict.items():
            if k.split('.')[0] in valid_keys:
                response_dict['updated_keys'][k] = v
    payload = model_tools.item_stringify(response_dict['updated_keys'])

    # Get abell ids of matching assets
    assets_to_update = asset_find(
                        asset_type,
                        asset_filter,
                        specified_keys={'_id': 0, 'abell_id': 1})
    assets_to_update = assets_to_update.get('result')
    if not multi:
        if len(assets_to_update) is not 1:
            response_dict.update({'error': 400,
                                  'message': 'The filter did not return '
                                             'a single asset'})
            return response_dict

    db_response = ABELLDB.update_asset(asset_type, asset_filter, payload)
    if db_response.get('success'):
        for a in assets_to_update:
            asset_id = a.get('abell_id')
            response_dict['updated_asset_ids'].append(asset_id)
        response_dict.update({'success': True,
                              'message': db_response.get('result')})
    # TODO Probably convert to a bulk find and update call
    # TODO Log updated documents
    return response_dict


def asset_find(asset_type, params, specified_keys=None):
    return ABELLDB.asset_find(asset_type, params, specified_keys)


def distinct_asset_fields(asset_type, params, distinct_key):
    return ABELLDB.asset_distinct(asset_type, params, str(distinct_key))


def asset_count(asset_type, params):
    return ABELLDB.asset_count(asset_type, params)


class AbellAsset(object):

    def __init__(self, asset_type, asset_info, abell_id, property_dict=None,
                 user_level='user'):
        self.asset_type = str(asset_type)
        self.abell_id = str(abell_id)
        self.asset_info = model_tools.item_stringify(asset_info)
        self.fields = {}

    def __getattr__(self, attr):
        if type(attr) == str:
            return 'None'
        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__, attr))

    def get_property(self, name):
        return getattr(self, name)

    def add_property_dict(self, property_dict):
        stringified_dict = model_tools.item_stringify(property_dict)
        for key, value in stringified_dict.iteritems():
            # self.add_property(key, value)
            setattr(self, key, value)

    def stringified_attributes(self):
        return model_tools.item_stringify(self.fields)

    def create_asset(self, asset_data):
        self.fields.update(dict.fromkeys(self.asset_info['system_keys']))
        self.fields.update(dict.fromkeys(self.asset_info['managed_keys']))
        self.fields.update(dict.fromkeys(self.asset_info['unmanaged_keys']))

        for key, value in asset_data.items():
            if key in self.fields:
                self.fields[key] = value
