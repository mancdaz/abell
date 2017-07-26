from abell import client
import requests
import requests_mock

import unittest
from unittest import mock


class TestAbellClient(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _attach_mock(self, client):
        adapter = requests_mock.Adapter()
        adapter.register_uri('GET', 'http://localhost:5000/api/v1/asset_type')
        client.mount('mock', adapter)

    def test_creation(self):
        c = client.AbellClient()
        self.assertIsInstance(c, requests.Session)

    def test_basic_get_asset_type(self):
        """Confirm that the `get` functions recieves the args we expected"""
        c = client.AbellClient()
        c.get = mock.Mock()
        c.get_asset_type('server')
        expected_params = {'type': 'server', 'managed_keys': None,
                           'unmanaged_keys': None}
        c.get.assert_called_with('http://localhost:5000/api/v1/asset_type',
                                 params=expected_params)


if __name__ == '__main__':
    unittest.main()
