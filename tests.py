from abell import create_app
from abell.config import test_config
import json

import unittest
from unittest import mock


class BasicRunningTestCase(unittest.TestCase):
    def setUp(self):
        with mock.patch('abell.mongo'):
            app = create_app(test_config)
            self.app = app.test_client()

    def tearDown(self):
        pass

    def test_hello_world(self):
        r = self.app.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, b'Hello')


class CreateAssetTypeTestCase(unittest.TestCase):
    def setUp(self):
        # insert server type!
        with mock.patch('abell.mongo'):
            app = create_app(test_config)
            self.app = app.test_client()
            self.app_context = app.app_context()
            self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @mock.patch('abell.database.mongo')
    def test_asset_info_without_type(self, mock_mongo):
        a = {'managed_keys': ['test'],
             'unmanaged_keys': ['test2']}
        r = self.app.post('/api/v1/asset_type',
                          data=json.dumps(a),
                          headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 400)

    @mock.patch('abell.models.asset_type.AbellAssetType')
    def test_asset_create(self, mock_at):
        mock_at.create_new_type.return_value = {'success': True}

        a = {'type': 'server',
             'managed_keys': ['test'],
             'unmanaged_keys': ['test2']}
        r = self.app.post('/api/v1/asset_type',
                          data=json.dumps(a),
                          headers={'content-type': 'application/json'})
        asset_type = a.pop('type')
        mock_at.called_with(asset_type, a)
        self.assertEqual(r.status_code, 200)

    @mock.patch('abell.models.asset_type.AbellAssetType')
    def test_duplicate_asset_type_create(self, mock_at):
        new_type = mock.Mock()
        new_type.create_new_type.return_value = {'success': True}
        # mock_at is called to create a new instance, which needs
        # to return a Mock with the appropriate methods.
        mock_at.return_value = new_type
        a = {'type': 'server',
             'managed_keys': ['test'],
             'unmanaged_keys': ['test2']}
        r = self.app.post('/api/v1/asset_type',
                          data=json.dumps(a),
                          headers={'content-type': 'application/json'})
        new_type.create_new_type.return_value = {'success': False}
        r = self.app.post('/api/v1/asset_type',
                          data=json.dumps(a),
                          headers={'content-type': 'application/json'})
        self.assertEqual(mock_at.call_count, 2)
        self.assertEqual(r.status_code, 400)


class GetAssetTypeTestCase(unittest.TestCase):
    def setUp(self):
        # insert server type!
        with mock.patch('abell.mongo'):
            app = create_app(test_config)
            self.app = app.test_client()
            self.app_context = app.app_context()
            self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @mock.patch('abell.models.asset_type.get_asset_type')
    def test_asset_info_get(self, mock_get):
        new_type = mock.Mock()
        new_type.key_dict.return_value = {
             'type': 'server',
             'managed_keys': ['test'],
             'unmanaged_keys': ['test2'],
        }
        mock_get.return_value = new_type
        r = self.app.get('/api/v1/asset_type?type=server')
        payload = dict(json.loads(r.data.decode()).get('payload'))
        self.assertEqual('server', payload.get('type'))

    def test_asset_info_get_nonexistent(self):
        r = self.app.get('/api/v1/asset_type?type=server')
        self.assertEqual(r.status_code, 404)


class DeleteAssetTypeTestCase(unittest.TestCase):
    def setUp(self):
        # insert server type!
        with mock.patch('abell.mongo'):
            app = create_app(test_config)
            self.app = app.test_client()
            self.app_context = app.app_context()
            self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_asset_delete_nonexistent(self):
        r = self.app.delete('/api/v1/asset_type?type=server')
        self.assertEqual(r.status_code, 404)

    @mock.patch('abell.models.asset_type.get_asset_type')
    def test_asset_delete(self, mock_get):
        mock_type = mock.Mock()
        mock_type.remove_type.return_value = {'success': True}
        mock_get.return_value = mock_type
        r = self.app.delete('/api/v1/asset_type?type=server')
        self.assertEqual(r.status_code, 200)
        mock_get.return_value = None
        r = self.app.get('/api/v1/asset_type?type=server')
        self.assertEqual(r.status_code, 404)
        # TODO Test for asset existence block


class UpdateAssetTypeTestCase(unittest.TestCase):
    def setUp(self):
        # insert server type!
        with mock.patch('abell.mongo'):
            app = create_app(test_config)
            self.app = app.test_client()
            self.app_context = app.app_context()
            self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @mock.patch('abell.models.asset_type.get_asset_type')
    def test_asset_type_delete_keys(self, mock_get):
        mock_type = mock.Mock()
        mock_type.update_keys.return_value = {'success': True,
                                              'removed_keys': ['test'],
                                              'new_keys': []
                                              }
        mock_get.return_value = mock_type
        u = {'type': 'server',
             'remove_keys': ['test']}
        r = self.app.put('/api/v1/asset_type',
                         data=json.dumps(u),
                         headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)
        mock_type.update_keys.assert_called_with(['test'], [], [])
        # test that its been removed from assets

    @mock.patch('abell.models.asset_type.AbellAssetType')
    def test_asset_type_swap_keys(self, mock_at):
        # TODO: This test needs to be revisited; it seems that we
        # should be using PUT to modify the asset type vs post...
        mock_type = mock.Mock()
        mock_type.return_value = mock.Mock()
        mock_type.return_value.create_new_type.return_value = {'success': True}
        mock_at.return_value = mock_type
        a = {'type': 'server',
             'managed_keys': ['test'],
             'unmanaged_keys': ['test2']}
        r = self.app.post('/api/v1/asset_type',
                          data=json.dumps(a),
                          headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)
        a.pop('type')
        mock_at.assert_called_with('server', asset_info=a)
        # test that its been removed from assets

    @mock.patch('abell.models.asset_type.get_asset_type')
    def test_asset_type_add_key(self, mock_get):
        mock_type = mock.Mock()
        mock_type.update_keys.return_value = {'success': True,
                                              'removed_keys': [],
                                              'new_keys': ['test3']
                                              }
        mock_get.return_value = mock_type
        u = {'type': 'server',
             'managed_keys': ['test3']}
        r = self.app.put('/api/v1/asset_type',
                         data=json.dumps(u),
                         headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)
        mock_type.update_keys.assert_called_with([], ['test3'], [])


if __name__ == '__main__':
    unittest.main()
