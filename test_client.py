from abell import client
import requests
import requests_mock

import unittest
from unittest import mock


ABELL_URI = 'http://localhost:5000/api/v1'


class TestAbellClient(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        try:
            # If any test used the mocking adapter, remove it.
            self.__dict__.pop('adapter')
        except KeyError:
            pass

    def _attach_mock(self, cli):
        self.adapter = requests_mock.Adapter()
        cli.mount('http://localhost:5000/', self.adapter)

    def _mock_response(self, method, path, return_data):
        self.adapter.register_uri(method, '/api/v1/' + path, json=return_data)

    def test_creation(self):
        c = client.AbellClient(ABELL_URI)
        self.assertIsInstance(c, requests.Session)

    def test_get_client_uri_building(self):
        c = client.get_client('localhost', '5000', 'api', 'v1')
        self.assertEqual(ABELL_URI, c.uri)

    def test_basic_get_asset_type(self):
        """Confirm that the `get` functions recieves the args we expected"""
        c = client.AbellClient(ABELL_URI)
        c.get = mock.Mock()
        c.get_asset_type('server')
        expected_params = {'type': 'server', 'managed_keys': None,
                           'unmanaged_keys': None}
        c.get.assert_called_with('http://localhost:5000/api/v1/asset_type',
                                 params=expected_params)

    def test_get_asset_type(self):
        cli = client.AbellClient(ABELL_URI)
        self._attach_mock(cli)
        data = {'code': 200, 'payload': {'type': 'server'}}
        self._mock_response('GET', 'asset_type?type=server', data)

        response = cli.get_asset_type('server')

        self.assertEqual(response, data)

    def test_create_server_type(self):
        """Tests making a basic server asset type."""
        cli = client.AbellClient(ABELL_URI)
        self._attach_mock(cli)
        ret_data = {'code': 200, 'payload': None,
                    'details': {'info': 'Asset type server created'}}
        self._mock_response('POST', 'asset_type?type=server', ret_data)

        response = cli.create_asset_type('server', ['versions', 'patches'],
                                         ['notes'])
        self.assertEqual(response, ret_data)


if __name__ == '__main__':
    unittest.main()
