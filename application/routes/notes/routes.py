from flask import (Flask, Blueprint, current_app, request, url_for, redirect, abort,
                    render_template, jsonify, send_file, flash, send_from_directory)
from application import db
import os
from application.forms.forms import NoteForm
from application.models.user import User
from flask_login import login_required, current_user
from application.models.note import Note
from application.routes.notes import bp
import uuid


DIR_PATH = 'application/static/files/'


@bp.route('/add-note', methods=["GET", "POST"])
@login_required
def add_note():
    user = current_user
    form = NoteForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        attachment = request.files[form.attachment.name]
        if attachment:
            user.add_note(title=title, description=description, attachment=attachment)
        else:
            user.add_note(title=title, description=description)
        flash('Note added successfully', category='success')
        return redirect(request.url)
    return render_template("add_note.html", form=form)

@bp.route('/private-notes/<string:file_hash>', methods=["GET", "POST"])
@login_required
def download_file_private(file_hash):
    file_to_download = Note.query.filter_by(attachment_hash=file_hash).first()
    if file_to_download:
        path_to_file = file_to_download.file_path
        current_app.logger.debug(path_to_file)
        org_filename = file_to_download.org_attachment_filename
        current_app.logger.debug(org_filename)
        try:
            return send_file(path_to_file, attachment_filename = org_filename, as_attachment = True)
        except Exception as e:
            current_app.logger.debug(e)

@bp.route('/public-notes/<string:file_hash>', methods=["GET", "POST"])
@login_required
def download_file_public(file_hash):
    file_to_download = Note.query.filter_by(attachment_hash=file_hash).first()
    if file_to_download:
        path_to_file = file_to_download.file_path
        org_filename = file_to_download.org_attachment_filename
        try:
            return send_file(path_to_file, attachment_filename = org_filename, as_attachment = True)
        except Exception as e:
            current_app.logger.debug(e)


@bp.route('/private-notes', methods=["GET", "POST"])
@login_required
def private_notes():
    page = request.args.get('page', 1, type=int)
    private_notes = current_user.notes.order_by(Note.timestamp.desc()).paginate(page, 5, False)
    next_url = url_for('notes.private_notes', page=private_notes.next_num) if private_notes.has_next else None
    prev_url = url_for('notes.private_notes', page=private_notes.prev_num) if private_notes.has_prev else None
    return render_template('private_notes.html', private_notes=private_notes.items, next_url=next_url, prev_url=prev_url)

@bp.route('/private-notes/make-public/<int:note_id>', methods=["GET", "POST"])
@login_required
def make_public(note_id):
    user = current_user
    note = Note.query.filter_by(id=note_id).first()
    if note.owner_id == user.id:
        note.is_public = True
        db.session.commit()
        flash('Note added to public notes.', category='info')
        return redirect(request.referrer)
    else:
        return redirect(url_for('dashboard.index'), 403)

@bp.route('/private-notes/delete/<int:note_id>', methods=["GET", "DELETE", "OPTIONS"])
@login_required
def delete_note(note_id):
    if request.method == 'DELETE':
        user = current_user
        note = Note.query.filter_by(id=note_id).first()
        if note.owner_id == user.id:
            if note.file_path:
                os.remove(note.file_path)
            db.session.delete(note)
            db.session.commit()
            response = jsonify('Note deleted')
            flash('Note deleted.', category='warning')   
        else:
            response = jsonify("You don't have permission to delete this note.")
    else:
        response = jsonify('Invalid method')
    return response

@bp.route('/private-notes/files/delete/<int:note_id>', methods=['OPTIONS', 'DELETE'])
@login_required
def delete_note_file(note_id):
    if request.method == 'DELETE':
        user = current_user
        note = Note.query.filter_by(id=note_id).first()
        if note.owner_id == user.id:
            path_to_file = note.file_path
            os.remove(path_to_file)
            note.file_path = note.attachment_hash = note.org_attachment_filename = None
            response = jsonify('File removed')
            db.session.commit() 
            flash('Attachment deleted.', category='warning')
        else:
            response = jsonify('File not found')
    return response

@bp.route('/private-notes/files/<int:note_id>', methods=['OPTIONS', 'PATCH'])
@login_required
def upload_note_file(note_id):
    if request.method == 'PATCH':
        user = current_user
        note = Note.query.filter_by(id=note_id).first()
        if note.owner_id == user.id:
            note_file = request.files['Note']
            note.upload_attachment(note_file)
            response = jsonify("File added.")
            flash('File uploaded successfully.', category='success')
        else:
            response = jsonify('Article not found')
    else:
        reponse = jsonify('Invalid method')
    return response

@bp.route('/private-notes/make-private/<int:note_id>', methods=["GET", "POST"])
@login_required
def make_private(note_id):
    user=current_user
    note=Note.query.filter_by(id=note_id).first()
    if note.owner_id == user.id:
        note.is_public = False
        db.session.commit()
        flash('Note changed to private.', category='info')
        return redirect(request.referrer)
    else:
        return redirect(url_for('dashboard.index'), 403)

@bp.route('/private-notes/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    title = 'Edit note'
    note = Note.query.get_or_404(note_id)
    form = NoteForm()
    if current_user.id != note.owner_id:
        abort(403)
    if form.validate_on_submit() and request.method == 'POST':
        if form.attachment.data:
            attachment = request.files[form.attachment.name]
            note.edit_note(title=form.title.data, description=form.description.data, 
                            attachment=attachment)
        else:
            note.edit_note(title=form.title.data, description=form.description.data)
        flash('Note edited successfully.', category='success')
        return redirect(request.referrer)
    form.title.data = note.title
    form.description.data = note.description
    return render_template('edit_note.html', form=form, title=title, note=note)

@bp.route('/subscribed-notes', methods=['GET'])
@login_required
def subscribed_notes(): 
    subscribed_notes = current_user.subscribed_notes
    return render_template('subscribed_notes.html', subscribed_notes=subscribed_notes)

@bp.route('/public-notes/subscribe/<int:note_id>', methods=["GET", "POST"])
@login_required
def subscribe_note(note_id):
    user = current_user
    note = Note.query.filter_by(id=note_id).first()
    if not note.is_subscribing(user):
        note.subscribe_note(user)
        db.session.commit()
        flash('Note added to subscribed notes.', category='info')
        return redirect(request.referrer)
    else:
        return redirect(url_for('main.index'))

@bp.route('/public-notes/unsubscribe/<int:note_id>', methods=["GET", "POST"])
@login_required
def unsubscribe_note(note_id):
    user = current_user
    note = Note.query.filter_by(id=note_id).first()
    if note.is_subscribing(user):
        note.unsubscribe_note(user)
        db.session.commit()
        flash('Note removed from subscribed notes.', category='info')
        return redirect(request.referrer)
    else:
        return redirect(url_for('main.index'))


@bp.route('/public-notes', methods=["GET"])
def public_notes():
    page = request.args.get('page', 1, type=int)
    notes = Note.query.filter_by(is_public=True).order_by(Note.timestamp.desc()).paginate(page, 5, False)
    next_url = url_for('notes.public_notes', page=notes.next_num) if notes.has_next else None
    prev_url = url_for('notes.public_notes', page=notes.prev_num) if notes.has_prev else None
    return render_template('public_notes.html', notes=notes.items, next_url=next_url, prev_url=prev_url)


@bp.route('/note/<int:note_id>', methods=['GET'])
@login_required
def note_detail(note_id):
    note = Note.query.get_or_404(note_id)
    if current_user.id == note.owner_id:
        return render_template('note_detail.html', is_owner = True, note=note)
    elif current_user.id != note.owner_id and note.is_public:
        return render_template('note_detail.html', is_owner = False, note=note)
    else:
        abort(403)
