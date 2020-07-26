from flask import Blueprint

bp = Blueprint('notes', __name__, static_folder='static')

from application.routes.notes import routes