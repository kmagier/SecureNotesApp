from flask import Flask, Blueprint, render_template, redirect, url_for, request
from functools import wraps

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register')
def register():
    return render_template('register.html')

@auth_bp.route('/login')
def login():
    return render_template('login.html')

@auth_bp.route('/change-password')
def change_password():
    return render_template('change-password.html')

@auth_bp.route('/logout')
def logout():
    return render_template('logout.html')

def get_username(sid):
    username = db.hget("session:" + sid, "username")
    return username 

def authorization_required(f):
    @wraps(f)
    def authorization_decorator(*args, **kwds):
        session_id = request.cookies.get('session_id', '')
        username = get_username(session_id)
        if not username or username == 'None':
            session["logged_in"] = False
            response = redirect(url_for('login'))
            response.set_cookie('session_id','', expires=0)
            return redirect(url_for('login'))
        return f(*args, **kwds)
    return authorization_decorator