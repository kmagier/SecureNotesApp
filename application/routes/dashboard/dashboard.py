from flask import Flask, Blueprint, render_template, redirect, url_for, session, request, current_app
# from routes.auth.auth import get_username

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    # session_id = request.cookies.get('session_id', '')
    # current_app.logger.debug(session_id)
    # username = get_username(session_id)
    # current_app.logger.debug(username)
    # if not username:
    #     session["logged_in"] = False
    # else:
    #     session["logged_in"] = True
    return render_template('index.html')