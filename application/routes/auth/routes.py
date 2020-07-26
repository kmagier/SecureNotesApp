from flask import (Flask, Blueprint, render_template, redirect, url_for, 
                    request, current_app, session, make_response, flash)
import random, string
from application.forms.forms import RegistrationForm, LoginForm, PasswordChangeForm, ResetPasswordRequestForm, ResetPasswordForm
from application import db
from application.routes.auth import bp
from application.models.user import User, check_existing_user
import bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from application.mailer import send_password_reset_email, send_registration_email

 
 
@bp.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        salt = bcrypt.gensalt(rounds=12)
        secure_password = bcrypt.hashpw(password.encode(), salt)
        email = form.email.data
        if not check_existing_user(username):
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            # send_registration_email(new_user)
            flash('Account created successfully', category='success')
            return redirect(url_for('auth.login'))
        flash('Could not register account. Username taken or wrong credentials', category='warning')
        return redirect(request.url)
    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(username=form.login.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Wrong username or password', category='warning')
        else:
            login_user(user)
            return redirect(url_for('main.index'))
    return render_template('auth/login.html', form=form)

@bp.route('/change-password', methods=["GET", "POST"])
@login_required
def change_password():
    form = PasswordChangeForm(request.form)
    user = current_user
    if request.method == 'POST' and form.validate_on_submit():  
        current_password = form.password.data
        new_password = form.new_password.data
        if not user.check_password(current_password):
            flash('Wrong password or passwords do not match.', category='warning')
            return redirect(request.url)
        else: 
            user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully', category='success')
            return redirect(url_for('main.index'))
    return render_template('auth/change_password.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', category='info')
    return redirect(url_for('main.index'))

@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit() and request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Email with link for password reset was sent.', category="info")
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', form=form)

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    if form.validate_on_submit() and request.method == 'POST':
        user.set_password(form.password.data)
        db.session.commit()
        flash('Password has been changed', category='info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

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