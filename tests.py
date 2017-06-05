from abell import create_app
from abell.config import test_config
from abell.database import AbellDb
import json
# from faker import Factory

import unittest

# fake = Factory.create()


class BasicRunningTestCase(unittest.TestCase):
    def setUp(self):
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
        app = create_app(test_config)
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        AbellDb().nuke_all_collections()

    def tearDown(self):
        self.app_context.pop()

    def test_asset_info_without_type(self):
        a = {'managed_keys': ['test'],
             'unmanaged_keys': ['test2']}
        r = self.app.post('/api/v1/asset_type',
                          data=json.dumps(a),
                          headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 400)

    def test_asset_create(self):
        a = {'type': 'server',
             'managed_keys': ['test'],
             'unmanaged_keys': ['test2']}
        r = self.app.post('/api/v1/asset_type',
                          data=json.dumps(a),
                          headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)

    def test_duplicate_asset_type_create(self):
        a = {'type': 'server',
             'managed_keys': ['test'],
             'unmanaged_keys': ['test2']}
        r = self.app.post('/api/v1/asset_type',
                          data=json.dumps(a),
                          headers={'content-type': 'application/json'})
        r = self.app.post('/api/v1/asset_type',
                          data=json.dumps(a),
                          headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 400)


class GetAssetTypeTestCase(unittest.TestCase):
    def setUp(self):
        # insert server type!
        app = create_app(test_config)
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        AbellDb().nuke_all_collections()

    def tearDown(self):
        self.app_context.pop()

    def test_asset_info_get(self):
        a = {'type': 'server',
             'managed_keys': ['test'],
             'unmanaged_keys': ['test2'],
             'system_keys': ['type', 'abell_id', 'cloud', 'owner']}
        self.app.post('/api/v1/asset_type',
                      data=json.dumps(a),
                      headers={'content-type': 'application/json'})
        r = self.app.get('/api/v1/asset_type?type=server')
        payload = dict(json.loads(r.data.decode()).get('payload'))
        self.assertEqual('server', payload.get('type'))
        if not (set(payload.get('managed_keys')) ==
                set(a.get('managed_keys'))):
            self.fail("managed_keys are not the same")
        if not (set(payload.get('unmanaged_keys')) ==
                set(a.get('unmanaged_keys'))):
            self.fail("unmanaged_keys are not the same")
        if not (set(payload.get('system_keys')) ==
                set(a.get('system_keys'))):
            self.fail("system_keys are not the same")

    def test_asset_info_get_nonexistent(self):
        r = self.app.get('/api/v1/asset_type?type=server')
        self.assertEqual(r.status_code, 404)


class DeleteAssetTypeTestCase(unittest.TestCase):
    def setUp(self):
        # insert server type!
        app = create_app(test_config)
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        AbellDb().nuke_all_collections()

    def tearDown(self):
        self.app_context.pop()

    def test_asset_delete_nonexistent(self):
        a = {'type': 'server'}
        r = self.app.delete('/api/v1/asset_type?type=server')
        self.assertEqual(r.status_code, 404)

    def test_asset_delete(self):
        a = {'type': 'server'}
        r = self.app.post('/api/v1/asset_type',
                          data=json.dumps(a),
                          headers={'content-type': 'application/json'})
        r = self.app.delete('/api/v1/asset_type?type=server')
        self.assertEqual(r.status_code, 200)
        r = self.app.get('/api/v1/asset_type?type=server')
        self.assertEqual(r.status_code, 404)
        # TODO Test for asset existence block


class UpdateAssetTypeTestCase(unittest.TestCase):
    def setUp(self):
        # insert server type!
        app = create_app(test_config)
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        AbellDb().nuke_all_collections()

    def tearDown(self):
        self.app_context.pop()

    def test_asset_type_delete_keys(self):
        a = {'type': 'server',
             'managed_keys': ['test'],
             'unmanaged_keys': ['test2']}
        r = self.app.post('/api/v1/asset_type',
                          data=json.dumps(a),
                          headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)
        u = {'type': 'server',
             'remove_keys': ['test']}
        r = self.app.put('/api/v1/asset_type',
                         data=json.dumps(u),
                         headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)
        r = self.app.get('/api/v1/asset_type?type=server')
        payload = dict(json.loads(r.data.decode()).get('payload'))
        self.assertEqual(payload.get('managed_keys'), [])
        # test that its been removed from assets

    def test_asset_type_swap_keys(self):
        a = {'type': 'server',
             'managed_keys': ['test'],
             'unmanaged_keys': ['test2']}
        r = self.app.post('/api/v1/asset_type',
                          data=json.dumps(a),
                          headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)
        u = {'type': 'server',
             'managed_keys': ['test2'],
             'unmanaged_keys': ['test']}
        r = self.app.put('/api/v1/asset_type',
                         data=json.dumps(u),
                         headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)
        r = self.app.get('/api/v1/asset_type?type=server')
        payload = dict(json.loads(r.data.decode()).get('payload'))
        self.assertEqual(payload.get('managed_keys'), ['test2'])
        self.assertEqual(payload.get('unmanaged_keys'), ['test'])
        # test that its been removed from assets

    def test_asset_type_add_key(self):
        a = {'type': 'server',
             'managed_keys': ['test'],
             'unmanaged_keys': ['test2']}
        r = self.app.post('/api/v1/asset_type',
                          data=json.dumps(a),
                          headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)
        u = {'type': 'server',
             'managed_keys': ['test3']}
        r = self.app.put('/api/v1/asset_type',
                         data=json.dumps(u),
                         headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)
        r = self.app.get('/api/v1/asset_type?type=server')
        payload = dict(json.loads(r.data.decode()).get('payload'))
        if not (set(payload.get('managed_keys')) ==
                set(['test', 'test3'])):
            self.fail("New managed key was not added")
        # test that its been updated from assets


if __name__ == '__main__':
    unittest.main()
