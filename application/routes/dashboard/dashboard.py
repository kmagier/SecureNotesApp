from datetime import datetime
from flask import Flask, Blueprint, render_template, redirect, url_for, session, request, current_app, flash
from flask_login import current_user, login_required
from models.user import User
from forms.forms import EditProfileForm
from database import db

bp = Blueprint('main', __name__)

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()

@bp.route('/index')
@bp.route('/')
def index():
    current_app.logger.debug(current_user)
    # session_id = request.cookies.get('session_id', '')
    # current_app.logger.debug(session_id)
    # username = get_username(session_id)
    # current_app.logger.debug(username)
    # if not username:
    #     session["logged_in"] = False
    # else:
    #     session["logged_in"] = True
    return render_template('index.html')

@bp.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    current_app.logger.debug(user.subscribed_notes)
    return render_template('user.html', user=user)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@bp.route('/follow/<int:user_id>', methods=['GET', 'POST'])
@login_required
def follow(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash('User {} not found.'.format(user.username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(request.referrer)
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(user.username))
    return redirect(request.referrer)

@bp.route('/unfollow/<int:user_id>', methods=['GET', 'POST'])
@login_required
def unfollow(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash('User {} not found.'.format(user.username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(request.referrer)
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(user.username))
    return redirect(request.referrer)
    



