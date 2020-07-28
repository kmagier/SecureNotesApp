from flask import Blueprint

bp = Blueprint('auth', __name__)

from application.routes.auth import routes