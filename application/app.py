from flask import Flask
import os
from database import db
from routes.auth.auth import auth_bp
from routes.dashboard.dashboard import dashboard_bp
from routes.notes.notes import notes_bp

app = Flask(__name__, static_url_path="")
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

app.register_blueprint(dashboard_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(notes_bp)

@app.errorhandler(403)
def page_forbidden(error):
    return render_template("errors/403.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html")