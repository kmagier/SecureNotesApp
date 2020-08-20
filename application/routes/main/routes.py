from datetime import datetime
from flask import Flask, Blueprint, render_template, redirect, url_for, session, request, current_app, flash, abort
from flask_login import current_user, login_required
from application.models.user import User
from application.models.note import Note
from application.models.post import Post
from application.forms.forms import EditProfileForm
from application import db
import os
from application.routes.main import bp

@bp.before_app_request
def before_request(): 
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()

@bp.route('/index')
@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, 2, False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    current_app.logger.debug(posts)
    return render_template('index.html', posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    notes = Note.query.filter_by(owner_id=user.id, is_public=True).order_by(Note.timestamp.asc()).all()
    current_app.logger.debug(notes)
    return render_template('user.html', user=user, notes=notes)

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
    return render_template('edit_profile.html', form=form, title="Edit info")

@bp.route('/follow/<int:user_id>', methods=['GET', 'POST'])
@login_required
def follow(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash(f'User {user.username} not found.', category='warning')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!', category='warning')
        return redirect(request.referrer)
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {user.username}!', category='info')
    return redirect(request.referrer)

@bp.route('/unfollow/<int:user_id>', methods=['GET', 'POST'])
@login_required
def unfollow(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash(f'User {user.username} not found.', category='warning')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!', category='warning')
        return redirect(request.referrer)
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {user.username}.', category='info')
    return redirect(request.referrer)

@bp.route('/user/<int:user_id>/notes')
@login_required
def user_notes(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    notes = Note.query.filter_by(owner_id=user.id, is_public=True).order_by(Note.timestamp.asc()).all()
    # return render_template('user.html', user=user)
    if notes:
        return render_template('public_user_notes_list.html', notes=notes, user=user)
    else:
        abort(404)

@bp.route('/user/<int:user_id>/followers')
@login_required
def user_followers_list(user_id):
    followers = current_user.followers.order_by(User.username.asc()).all()
    return render_template('user_followers.html', followers_template=True, followers=followers, title='FOLLOWERS')
    

@bp.route('/user/<int:user_id>/is_following')
@login_required
def user_followed_list(user_id):
    followed = current_user.followed.order_by(User.username.asc()).all()
    return render_template('user_followers.html', followed_template=True, followed=followed, title='FOLLOWED')



