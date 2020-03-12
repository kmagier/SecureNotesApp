from flask import (Flask, Blueprint, render_template, redirect, url_for, 
                    request, current_app, session, make_response, flash)
from functools import wraps
from forms.forms import *
from database import db
import bcrypt
import random, string
from const import *

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        salt = bcrypt.gensalt(rounds=12)
        secure_password = bcrypt.hashpw(password.encode(), salt)
        current_app.logger.debug("Bcrypt salt %s" % salt)
        current_app.logger.debug("Bcrypt password %s" % secure_password)
        email = form.email.data
        user_id = db.incr(USER_ID)
        db.hset("user:" + username, SALT, salt)
        db.hset("user:" + username, USER_ID, user_id)
        db.hset("user:" + username, USER_LOGIN, username)
        db.hset("user:" + username, USER_EMAIL, email)
        db.hset("user:" + username, USER_PASSWORD, secure_password)
        db.lpush(USERS, username)
        current_app.logger.debug("Username: %s" % username)
        current_app.logger.debug("Email: %s" % email)
        current_app.logger.debug("Password: %s" % password)
        current_app.logger.debug("Secure password: %s" % secure_password)
        current_app.logger.debug(db.hget("user:" + username, SALT))
        current_app.logger.debug(db.hget("user:" + username, USER_PASSWORD))
        return redirect(url_for('dashboard.index'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
        if form.login.data not in db.lrange(USERS, 0, -1):
            current_app.logger.debug("Nie ma takiego uzytkownika")
        else:
            username = form.login.data
            password = form.password.data
            salt = db.hget("user:" + username, SALT)
            secure_password = bcrypt.hashpw(password.encode(), salt.encode())
            current_app.logger.debug("Username: %s" % username)
            current_app.logger.debug("Secure password: %s" % secure_password)
            if username == db.hget("user:" + username, USER_LOGIN) and secure_password == db.hget("user:" + username, USER_PASSWORD).encode():
                session_id = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=15))
                current_app.logger.debug(session_id)
                db.hset("session:" + session_id, "username", username)
                session["logged_in"] = True
                response = make_response(redirect(url_for('dashboard.index')), 303)
                response.set_cookie("session_id", session_id, max_age=120)
                return response
            return redirect(url_for('dashboard.index'))
    return render_template('login.html', form=form)

@auth_bp.route('/change-password', methods=["GET", "POST"])
def change_password():
    form = PasswordChangeForm(request.form)
    session_id = request.cookies.get('session_id', '')
    username = get_username(session_id)
    if not username or username=='None':
        return redirect(url_for('auth.login'))
    if request.method == 'POST' and form.validate_on_submit():  
        current_password = form.password.data
        new_password = form.new_password.data
        old_salt = db.hget("user:" + username, SALT)
        new_salt = bcrypt.gensalt()
        current_app.logger.debug("Current password: %s " % db.hget("user:" + username, USER_PASSWORD))
        if bcrypt.hashpw(current_password.encode(), old_salt.encode()) == db.hget("user:" + username, USER_PASSWORD).encode():
            new_secure_password = bcrypt.hashpw(new_password.encode(), new_salt)
            db.hset("user:" + username, USER_PASSWORD, new_secure_password)
            db.hset("user:" + username, SALT, new_salt)
            current_app.logger.debug("New password: %s" % new_secure_password)
            flash("Password changed")
            return redirect(url_for('dashboard.index'))
        else: 
            return redirect(request.url)
    return render_template('change-password.html', form=form)

@auth_bp.route('/logout')
def logout():
    session_id = request.cookies.get('session_id')
    db.delete("session:" + session_id)
    session["logged_in"] = False
    response = make_response(redirect(url_for('dashboard.index')))
    response.set_cookie("session_id", "", expires=0)
    return response

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