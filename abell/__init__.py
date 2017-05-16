from flask import Flask, g
from abell.database import mongo
from abell import config
from abell.api import api
import time


def create_app(config=config.base_config):
    app = Flask(__name__)
    app.config.from_object(config)

    register_extensions(app)
    register_blueprints(app)

    @app.before_request
    def before_request():
        g.request_start_time = time.time()
        g.request_time = lambda: '%.5fs' % (time.time() - g.request_start_time)

    @app.route('/', methods=['GET'])
    def index():
        return 'Hello'

    return app


def register_extensions(app):
    mongo.init_app(app)


def register_blueprints(app):
    app.register_blueprint(api, url_prefix='/api')
