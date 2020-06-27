from flask import (Flask, Blueprint, render_template, redirect, url_for, 
                    request, current_app, session, make_response, flash)
from functools import wraps
from forms.forms import *
from database import db
from models.user import User, check_existing_user
import bcrypt
from app import login_manager
from flask_login import login_user, logout_user, current_user, login_required
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
        existing_user = check_existing_user(username)
        current_app.logger.debug(f'User exists:{existing_user}')
        if check_existing_user(username) is False:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            current_app.logger.debug(f'Created user {username} with email {email} and password {password}')
        return redirect(url_for('dashboard.index'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(username=form.login.data).first()
        if user is None or not user.check_password(form.password.data):
            current_app.logger.debug('Wrong username or password')
        else:
            login_user(user)
            current_app.logger.debug(f'Found user with name:{user} and password{user.password_hash}')
            return redirect(url_for('dashboard.index'))
    return render_template('login.html', form=form)

@auth_bp.route('/change-password', methods=["GET", "POST"])
@login_required
def change_password():
    form = PasswordChangeForm(request.form)
    user = current_user
    if request.method == 'POST' and form.validate_on_submit():  
        current_password = form.password.data
        new_password = form.new_password.data
        if not user.check_password(current_password):
            return redirect(request.url)
        else: 
            user.set_password(new_password)
            db.session.commit()
            return redirect(url_for('dashboard.index'))
    return render_template('change-password.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('dashboard.index'))



# def authorization_required(f):
#     @wraps(f)
#     def authorization_decorator(*args, **kwds):
#         session_id = request.cookies.get('session_id', '')
#         username = get_username(session_id)
#         if not username or username == 'None':
#             session["logged_in"] = False
#             response = redirect(url_for('auth.login'))
#             response.set_cookie('session_id','', expires=0)
#             return response
#         return f(*args, **kwds)
#     return authorization_decorator