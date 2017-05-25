from flask import Blueprint

api = Blueprint('api', __name__)

from abell.api import v1_controller  # noqa
