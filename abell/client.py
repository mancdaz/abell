import requests


def get_client(host, port, path, version):
    format_tmpl = 'http://{host}:{port}/{api_path}/{version}'
    uri = format_tmpl.format(host=host,
                             port=port,
                             api_path=path,
                             version=version)
    return AbellClient(uri)


class AbellClient(requests.Session):
    def __init__(self, uri, *args, **kwargs):
        self.uri = uri
        self.headers = {'content-type': 'application/json'}
        super(AbellClient, self).__init__(*args, **kwargs)

    def get_asset_type(self, type_name, managed_keys=None,
                       unmanaged_keys=None):
        endpoint = "{api_uri}/asset_type".format(api_uri=self.uri)
        params = {'type': type_name, 'managed_keys': managed_keys,
                  'unmanaged_keys': unmanaged_keys}
        resp = self.get(endpoint, params=params)
        return resp.json()

    def create_asset_type(self, type_name, managed_keys=None,
                          unmanaged_keys=None):
        endpoint = "{api_uri}/asset_type".format(api_uri=self.uri)
        params = {'type': type_name, 'managed_keys': managed_keys,
                  'unmanaged_keys': unmanaged_keys}
        resp = self.post(endpoint, params=params)
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
