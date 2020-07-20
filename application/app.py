from flask import (Flask, request, render_template, redirect, url_for,
    send_file, make_response, session, flash)
import os
import psycopg2
from database import db
from config import *
from flask_login import LoginManager


app = Flask(__name__, static_url_path="")
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

login_manager=LoginManager()
db.app = app 
db.metadata.clear()

from routes.auth.auth import auth_bp
from routes.dashboard.dashboard import bp as dashboard_bp
from routes.notes.notes import notes_bp
from routes.admin.views import bp as admin_bp
from models.user import User
from models.note import Note
db.init_app(app) 
login_manager.init_app(app)

db.create_all()


app.register_blueprint(dashboard_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(admin_bp)

@app.errorhandler(403)
def page_forbidden(error):
    return render_template("errors/403.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html")