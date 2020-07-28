from flask import Blueprint

bp = Blueprint('admin', __name__, url_prefix='/admin')

from application.routes.admin import routes