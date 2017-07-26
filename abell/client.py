import requests

ABELL_IP = 'localhost'
ABELL_PORT = '5000'
ABELL_PATH = 'api'
ABELL_VERSION = 'v1'
format_tmpl = 'http://{ip}:{port}/{api_path}/{version}'
ABELL_URI = format_tmpl.format(ip=ABELL_IP,
                               port=ABELL_PORT,
                               path=ABELL_PATH,
                               version=ABELL_VERSION)


class AbellClient(requests.Session):
    def __init__(self):
        self.uri = ABELL_URI
        self.headers = {'content-type': 'application/json'}

    def get(self, *args, **kwargs):
        super(AbellClient).get(*args, **kwargs, headers=self.headers)

    def get_asset_type(self, type_name, managed_keys=None,
                       unmanaged_keys=None):
        endpoint = "{api_uri}/asset_type".format(api_uri=self.uri)
        params = {'type': type_name, 'managed_keys': managed_keys,
                  'unmanaged_keys': unmanaged_keys}
        resp = self.get(endpoint, params=params)
        return resp.json()

    def get_asset(self):
        pass

    def update_asset(self):
        pass

    def update_asset_type(self, type_name, remove_keys=None, managed_keys=None,
                          unmanaged_keys=None):
        pass

    def delete_asset_type(self, type_name):
        pass
