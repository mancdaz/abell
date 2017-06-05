import os


class base_config(object):
    """Default configuration options."""
    SITE_NAME = 'Abell'

    MONGO_HOST = os.environ.get('MONGO_HOST', '127.0.0.1')
    MONGO_PORT = os.environ.get('MONGO_PORT', '27017')
    MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'abell')
    MONGO_USERNAME = os.environ.get('MONGO_USERNAME', 'abell')
    MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', '123456')


class dev_config(base_config):
    """Development configuration options."""
    DEBUG = True
    ASSETS_DEBUG = True
    WTF_CSRF_ENABLED = False


class test_config(base_config):
    """Testing configuration options."""
    TESTING = True
    MONGO_HOST = os.environ.get('MONGO_HOST', '127.0.0.1')
    MONGO_PORT = os.environ.get('MONGO_PORT', '27017')
    MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'abell')
    MONGO_USERNAME = os.environ.get('MONGO_USERNAME', 'abell')
    MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', '123456')
