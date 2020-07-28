from flask import Blueprint

bp = Blueprint('errors', __name__)

from application.routes.errors import handlers