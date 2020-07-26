from flask import render_template, request
from application import db
from application.routes.errors import bp

@bp.errorhandler(403)
def page_forbidden(error):
    return render_template("errors/403.html"), 403

@bp.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404