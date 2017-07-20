from flask_pymongo import PyMongo

mongo = PyMongo()


class AbellDb(object):
    def get_asset_type_info(self, asset_type):
        response_dict = {'success': False}
        try:
            asset_info = mongo.db.assetinfo.find_one({'type': asset_type},
                                                     {'_id': False})
            response_dict.update({'success': True,
                                  'result': asset_info})
        except Exception as e:
            response_dict.update(
                {'error': 500,
                 'message': 'Unknown db error, contact admin'})
            # (TODO) log error
            print(e)
            return response_dict
        return response_dict

    def update_managed_vars(self, asset_type, update_dict):
        response_dict = {'success': False}
        try:
            mongo.db.assetinfo.update_one({'type': asset_type},
                                          {'$set': update_dict})
            response_dict.update({'success': True})
        except Exception as e:
            response_dict.update(
                {'error': 500,
                 'message': 'Error in managed keys update, contact admin'})
            # (TODO) log error
            print(e)
            return response_dict
        return response_dict

    def update_asset_type(self, update_dict):
        response_dict = {'success': False}
        asset_type = update_dict.get('type')
        try:
            mongo.db.assetinfo.update_one({'type': asset_type},
                                          {'$set': update_dict})
            response_dict.update({'success': True})
        except Exception as e:
            response_dict.update(
                {'error': 500,
                 'message': 'Error in managed keys update, contact admin'})
            # (TODO) log error
            print(e)
            return response_dict
        return response_dict

    def add_new_asset_type(self, initial_keys):
        response_dict = {'success': False}
        asset_type = initial_keys.get('type')
        try:
            mongo.db.assetinfo.insert_one(initial_keys)
            mongo.db.create_collection(asset_type)
            mongo.db[asset_type].create_index('abell_id', unique=True)
            response_dict.update({'success': True})
            return response_dict
        except Exception as e:
            print(e)
            return response_dict

    def add_new_key_all_assets(self, asset_type, new_vars):
        # adds new field to all assets of a given type
        response_dict = {'success': False}

        new_var_dict = dict((k, 'None') for k in new_vars)
        try:
            resp = mongo.db[asset_type].update_many({},
                                                    {'$set': new_var_dict})
            if resp.acknowledged is True:
                response_dict.update({'success': True})
                return response_dict
            else:
                response_dict.update({'error': 500,
                                      'message':
                                          'Unknown update all assets error'})
        except Exception as e:
            response_dict.update(
                {'error': 500,
                 'message': 'Unknown db error, contact admin'})
            # (TODO) log error
            print(e)
        return response_dict

    def delete_key_all_assets(self, asset_type, remove_keys):
        response_dict = {'success': False}

        remove_dict = dict((k, "") for k in remove_keys)
        try:
            resp = mongo.db[asset_type].update_many({},
                                                    {'$unset': remove_dict})
            if resp.acknowledged is True:
                response_dict.update({'success': True})
                return response_dict
            else:
                response_dict.update({'error': 500,
                                      'message':
                                          'Unknown update all assets error'})
        except Exception as e:
            response_dict.update(
                {'error': 500,
                 'message': 'Unknown db error, contact admin'})
            # (TODO) log error
            print(e)
        return response_dict

    def add_new_asset(self, payload):
        response_dict = {'success': False}
        asset_type = payload.get('type')
        abell_id = payload.get('abell_id')
        if not asset_type or not abell_id:
            response_dict.update(
                {'error': 400,
                 'message':
                    'Did not recieve asset_type or abell_id for insert'})
            return response_dict
        try:
            resp = mongo.db[asset_type].insert_one(payload)
            if resp.acknowledged is True:
                response_dict.update({'success': True,
                                      'message': 'asset with abell_id: %s '
                                                 'created' % abell_id})
                return response_dict
        except Exception as e:
            if 'duplicate key error' in str(e):
                response_dict.update(
                    {'error': 400,
                     'message': 'abell_id: %s already exists in the '
                                'database' % abell_id})
            else:
                response_dict.update(
                    {'error': 500,
                     'message': 'Unknown db, contact admin'})
            return response_dict

    def asset_find(self, asset_type, asset_filter, specified_keys=None):
        response_dict = {'success': False,
                         'error': None,
                         'message': None,
                         'result': None}
        try:
            if specified_keys:
                result = mongo.db[asset_type].find(
                            asset_filter,
                            specified_keys).batch_size(50)
                response_dict.update(
                    {'success': True,
                     'result': list(result)})
            else:
                result = mongo.db[asset_type].find(asset_filter).batch_size(50)
                response_dict.update(
                    {'success': True,
                     'result': list(result)})
        except Exception as e:
            print(e)
            response_dict.update(
                {'error': 500,
                 'message': 'DB Find Error'})
        return response_dict

    def asset_count(self, asset_type, asset_filter):
        response_dict = {'success': False}
        try:
            result = mongo.db[asset_type].find(
                        asset_filter).count()
            response_dict.update(
                {'success': True,
                 'result': result})
        except Exception as e:
            print(e)
            response_dict.update(
                {'error': 500,
                 'message': 'DB Count Error'})
        return response_dict

    def asset_distinct(self, asset_type, asset_filter, distinct_attribute):
        response_dict = {'success': False,
                         'error': None,
                         'message': None,
                         'result': None}
        try:
            result = mongo.db[asset_type].find(
                        asset_filter).distinct(distinct_attribute)
            response_dict.update(
                {'success': True,
                 'result': result})
        except Exception as e:
            print(e)
            response_dict.update(
                {'error': 500,
                 'message': 'DB distinct Error'})
        return response_dict

    def update_asset(self, asset_type, asset_filter, update_dict):
        response_dict = {'success': False,
                         'error': None,
                         'message': None,
                         'result': None}
        try:
            result = mongo.db[asset_type].update_many(asset_filter,
                                                      {'$set': update_dict})
            if result.acknowledged:
                response_dict['success'] = True
                response_dict['result'] = '%s matched, %s modified' % (
                                            result.matched_count,
                                            result.modified_count)
        except Exception as e:
            print(e)
            response_dict['error'] = 'DB update error'
            return response_dict

        return response_dict

    def delete_assets(self, asset_type, asset_filter):
        response_dict = {'success': False}
        try:
            result = mongo.db[asset_type].delete_many(asset_filter)
            if result.acknowledged:
                response_dict['success'] = True
        except Exception as e:
            print(e)
            response_dict['error'] = 'DB delete error'
            return response_dict

        return response_dict

    def delete_asset_type(self, asset_type):
        response_dict = {'success': False}
        try:
            mongo.db.drop_collection(asset_type)
            result = mongo.db.assetinfo.delete_one({'type': asset_type})

            if result.acknowledged:
                response_dict['success'] = True
        except Exception as e:
            print(e)
            response_dict['error'] = 'DB delete error'
            return response_dict

        return response_dict

    def nuke_all_collections(self):
        collections = mongo.db.collection_names()
        for c in collections:
            mongo.db.drop_collection(c)
