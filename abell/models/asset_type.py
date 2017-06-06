from abell.models import model_tools
from abell.database import AbellDb


ABELLDB = AbellDb()


def get_asset_type(asset_type):
    # need to cache this!
    db_response = ABELLDB.get_asset_type_info(asset_type).get('result')
    if not db_response:
        return None
    asset_type = AbellAssetType(asset_type, asset_info=db_response)
    return asset_type


class AbellAssetType(object):
    SYSTEM_KEYS = ['cloud', 'owner', 'type', 'abell_id']

    def __init__(self, asset_type, asset_info={}):
        self.asset_type = asset_type
        self.managed_keys = set(asset_info.get('managed_keys', []))
        self.unmanaged_keys = set(asset_info.get('unmanaged_keys', []))
        self.system_keys = set(asset_info.get('system_keys', self.SYSTEM_KEYS))

    def key_dict(self):
        return {'type': self.asset_type,
                'managed_keys': list(self.managed_keys),
                'unmanaged_keys': list(self.unmanaged_keys),
                'system_keys': list(self.system_keys)}

    def __update_database(self, case, **kwargs):
        if case is 'new_keys':
            new_keys = kwargs.get('new_keys')
            update_dict = {'managed_keys': list(self.managed_keys)}
            db_resp = ABELLDB.update_managed_vars(self.asset_type, update_dict)
            if not db_resp.get('success'):
                return db_resp
            db_resp = ABELLDB.add_new_key_all_assets(self.asset_type,
                                                     list(new_keys))
            return db_resp

        elif case is 'new_type':
            update_dict = {'type': self.asset_type,
                           'managed_keys': list(self.managed_keys),
                           'unmanaged_keys': list(self.unmanaged_keys),
                           'system_keys': list(self.system_keys)}
            db_resp = ABELLDB.add_new_asset_type(update_dict)
            return db_resp

        elif case is 'delete_type':
            db_resp = ABELLDB.delete_asset_type(self.asset_type)
            return db_resp

        elif case is 'update_type':
            new_keys = kwargs.get('new_keys')
            removed_keys = kwargs.get('removed_keys')
            # update type
            db_resp = ABELLDB.update_asset_type(self.key_dict())
            if not db_resp.get('success'):
                return db_resp
            # add new keys
            if new_keys:
                db_resp = ABELLDB.add_new_key_all_assets(self.asset_type,
                                                         list(new_keys))
                if not db_resp.get('success'):
                    return db_resp
            # remove keys
            if removed_keys:
                db_resp = ABELLDB.delete_key_all_assets(self.asset_type,
                                                        list(removed_keys))
            return db_resp

        return {'success': False}

    def add_new_keys(self, new_keys=[]):
        given_keys = set(new_keys)
        all_keys = self.unmanaged_keys.union(self.managed_keys)
        all_keys.update(self.system_keys)
        new_keys = given_keys.difference(all_keys)
        if not new_keys:
            return {'success': True, 'new_keys': new_keys}
        self.managed_keys.update(new_keys)
        r = self.__update_database('new_keys', new_keys=list(new_keys))
        if r.get('success'):
            return {'success': True, 'new_keys': new_keys}
        return r

    def create_new_type(self, managed_keys=[], unmanaged_keys=[]):
        # check if type exists
        type_check = get_asset_type(self.asset_type)
        if type_check:
            return {'success': False,
                    'message': '%s type already exists' % self.asset_type}

        self.managed_keys.update(managed_keys)
        self.unmanaged_keys.update(unmanaged_keys)
        r = self.__update_database('new_type')
        return r
        # log & posible hooks

    def remove_type(self):
        # check if there are any assets of this type in the db
        r = ABELLDB.asset_count(self.asset_type, {})
        if not r.get('success'):
            return {'success': False}
        asset_count = r.get('result')
        if asset_count == 0:
            r = self.__update_database('delete_type')
            return r
        return {'success': False,
                'message': 'There are still assets of this type in the '
                'DB. Remove all assets of type %s then '
                'resubmit this call' % self.asset_type}

    def update_keys(self, remove_keys=[], managed_keys=[], unmanaged_keys=[]):
        all_removed_keys = set([])
        all_new_keys = set([])

        if remove_keys:
            managed_removal = self.managed_keys.intersection(set(remove_keys))
            unmanaged_removal = self.unmanaged_keys.intersection(
                                                    set(remove_keys))
            self.managed_keys.difference_update(managed_removal)
            self.unmanaged_keys.difference_update(unmanaged_removal)
            all_removed = managed_removal.union(unmanaged_removal)
            all_removed_keys.update(all_removed)
            # delete all keys from asset type

        if managed_keys:
            all_user_avail_keys = self.managed_keys.union(self.unmanaged_keys)
            # filter system keys
            managed_update = set(managed_keys).difference(self.system_keys)
            # identify brand new keys
            new_keys = managed_update.difference(all_user_avail_keys)
            all_new_keys.update(new_keys)
            # remove from unmanaged_keys
            self.unmanaged_keys.difference_update(managed_update)
            # update managed_keys
            self.managed_keys.update(managed_update)
            # update new keys

        if unmanaged_keys:
            all_user_avail_keys = self.managed_keys.union(self.unmanaged_keys)
            # filter system keys
            unmanaged_update = set(unmanaged_keys).difference(self.system_keys)
            # identify brand new keys
            new_keys = unmanaged_update.difference(all_user_avail_keys)
            all_new_keys.update(new_keys)
            # remove from managed_keys
            self.managed_keys.difference_update(unmanaged_update)
            # update unmanaged_keys
            self.unmanaged_keys.update(unmanaged_update)
            # print(managed_update)
            # update new keys
        r = self.__update_database('update_type', new_keys=all_new_keys,
                                   removed_keys=all_removed_keys)
        if r.get('success'):
            return {'success': True,
                    'removed_keys': list(all_removed_keys),
                    'new_keys': list(all_new_keys)}
        return {'success': False,
                'message': r.get('message', 'Unknown update error')}
