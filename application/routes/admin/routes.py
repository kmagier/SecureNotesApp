from flask import Flask, Blueprint, render_template, redirect, url_for, session, request, current_app, flash, abort
from flask_login import current_user, login_required
from application.models.user import User
from application.models.note import Note
from application.models.post import Post
from application import db
import random, string, os
from .forms import AdminEditProfileForm, AdminEditNoteForm, AdminPostForm
from application.routes.admin import bp
from functools import wraps
import uuid


DIR_PATH = 'static/files/'

def admin_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if not current_user.is_admin:
            flash("You don't have permission", category='warning')
            abort(403)
        return f(*args, **kwargs)
    return func

@bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/admin_dashboard.html')

@bp.route('/users')
@login_required
@admin_required
def admin_user_list():
    users = User.query.order_by(User.registered_date.asc()).all()
    return render_template('admin/admin_user_manager.html', users=users)

@bp.route('/notes')
@login_required
@admin_required
def admin_notes_list():
    notes = Note.query.order_by(Note.timestamp.asc()).all()
    return render_template('admin/admin_notes_manager.html', notes=notes)

@bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_user_edit(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminEditProfileForm(user.username)
    if request.method == 'POST' and form.validate_on_submit:
        user.username = form.username.data
        user.email = form.email.data
        user.about_me = form.about_me.data
        user.is_admin = form.is_admin.data
        db.session.commit()
    form.username.data = user.username
    form.email.data = user.email
    form.about_me.data = user.about_me
    form.is_admin.data = user.is_admin
    return render_template('admin/admin_user.html', form=form, title=f'Edit user')

@bp.route('/users/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_user_delete(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin.admin_user_list'))
    return render_template('admin/admin_delete.html', title='Delete user', user=user)

@bp.route('/notes/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_note_edit(note_id):
    note = Note.query.get_or_404(note_id)
    form = AdminEditNoteForm(obj=note)
    if request.method == 'POST' and form.validate_on_submit():
        if form.attachment.data:
            attachment = request.files[form.attachment.name]
            if(len(attachment.filename) > 0): 
                filename_prefix = str(uuid.uuid4())  
                new_filename = filename_prefix + '.' + attachment.filename.split('.')[-1]
                path_to_file = os.path.join(current_app.static_folder, 'files', new_filename)
                attachment.save(path_to_file)   
                note.attachment_hash = new_filename
                note.file_path = path_to_file
                note.org_attachment_filename = attachment.filename
        note.title = form.title.data
        note.description = form.description.data
        db.session.commit()
        return redirect(url_for('admin.admin_notes_list'))
    form.title.data = note.title
    form.description.data = note.description
    return render_template('admin/admin_note.html', form=form, title='Admin note edit', note=note)

@bp.route('/notes/delete/<int:note_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_note_delete(note_id):
    note = Note.query.get_or_404(note_id)
    form = AdminEditNoteForm(obj=note)
    if request.method == 'POST':
        if note.file_path:
            os.remove(note.file_path)
        db.session.delete(note)
        db.session.commit()
        return redirect(url_for('admin.admin_notes_list'))
    return render_template('admin/admin_delete.html', form=form, title='Delete note', note=note)


@bp.route('/post', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_post():
    form = AdminPostForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('admin/admin_post.html', form=form)

@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_post_edit(post_id):
    post = Post.query.get_or_404(post_id)
    form = AdminPostForm(obj=post)
    if request.method == 'POST' and form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('admin/admin_post.html', form=form)

@bp.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        db.session.delete(post)
        db.session.commit()
        return redirect(request.referrer)
    return redirect(url_for('main.index'))



