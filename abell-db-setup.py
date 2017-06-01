from pymongo import MongoClient

client = MongoClient('localhost:27017')
client.admin.authenticate('admin', 'password')
client.abell.add_user('abell', '123456',
                      roles=[{'role': 'readWrite', 'db': 'abell'}])
db = client['abell']
db['assetinfo'].create_index('type', unique=True)
