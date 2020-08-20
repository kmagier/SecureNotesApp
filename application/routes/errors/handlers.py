from flask import render_template, request
from application.routes.errors import bp

@bp.app_errorhandler(403)
def page_forbidden(error):
    return render_template("errors/403.html"), 403

@bp.app_errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404