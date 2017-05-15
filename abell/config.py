import os


class base_config(object):
    """Default configuration options."""
    SITE_NAME = 'Abell'

    MONGO_HOST = '127.0.0.1'
    MONGO_PORT = '27017'
    MONGO_DBNAME = 'abell'
    MONGO_USERNAME = 'abell'
    MONGO_PASSWORD = '123456'
    # SERVER_NAME = os.environ['SERVER_NAME']
    # SECRET_KEY = os.environ['SECRET_KEY']

    # CACHE_HOST = os.environ['MEMCACHED_PORT_11211_TCP_ADDR']
    # CACHE_PORT = os.environ['MEMCACHED_PORT_11211_TCP_PORT']


class dev_config(base_config):
    """Development configuration options."""
    DEBUG = True
    ASSETS_DEBUG = True
    WTF_CSRF_ENABLED = False


class test_config(base_config):
    """Testing configuration options."""
    TESTING = True
    WTF_CSRF_ENABLED = False
