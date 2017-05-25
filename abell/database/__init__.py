from flask_pymongo import PyMongo

mongo = PyMongo()


class AbellDb(object):
    def get_asset_info(self, asset_type):
        asset_info = mongo.db.assetinfo.find_one({'type': asset_type},
                                                 {'_id': False})
        return asset_info

    def update_managed_vars(self, asset_type, new_vars):
        mongo.db.assetinfo.update({'type': asset_type},
                                  {'$addToSet': {'managed_keys':
                                   {'$each': new_vars}}})

    def add_new_key(self, asset_type, new_vars):
        # adds new field to all assets of a given type
        response_dict = {'success': False,
                         'error': None,
                         'message': None}

        new_var_dict = dict((k, 'None') for k in new_vars)
        try:
            resp = mongo.db[asset_type].update_many({},
                                                    {'$set': new_var_dict})
            if resp.acknowledged is True:
                response_dict.update(
                    {'success': True,
                     'message': new_vars})
                return response_dict
        except Exception as e:
            response_dict.update(
                {'error': 500,
                 'message': 'Unknown db error, contact admin'})
            # (TODO) log error
            print(e)
            return response_dict

    def add_new_asset(self, payload):
        response_dict = {'success': False,
                         'error': None,
                         'message': None}
        asset_type = payload.get('type')
        abell_id = payload.get('abell_id')
        if not asset_type:
            response_dict.update(
                {'error': 400,
                 'message': 'Did not recieve asset_type for insert'})
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
                     'result': result})
            else:
                result = mongo.db[asset_type].find(asset_filter).batch_size(50)
                response_dict.update(
                    {'success': True,
                     'result': result})
        except Exception as e:
            print(e)
            response_dict.update(
                {'error': 500,
                 'message': 'DB Find Error'})
        return response_dict

    def asset_count(self, asset_type, asset_filter):
        response_dict = {'success': False,
                         'error': None,
                         'message': None,
                         'result': None}
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
        result = 0
        try:
            print(update_dict)
            result = mongo.db[asset_type].update_many(
                        asset_filter,
                        {'$set': update_dict})
            print(result.raw_result)
        except Exception as e:
            print(e)

        return result
