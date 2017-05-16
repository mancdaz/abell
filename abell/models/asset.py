# from repoze.lru import lru_cache
import model_tools


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

        for key, value in asset_data.iteritems():
            if key in self.fields:
                self.fields[key] = value
