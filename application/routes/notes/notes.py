from flask import (Flask, Blueprint, current_app, request, url_for, redirect, 
                    render_template, jsonify, send_file, flash)
from database import db
import os
from forms.forms import NoteForm
from models.user import User
from flask_login import login_required, current_user
from models.note import Note
import uuid


notes_bp = Blueprint('notes', __name__, static_folder='static')
DIR_PATH = 'static/files/'

@notes_bp.route('/add-note', methods=["GET", "POST"])
@login_required
def add_note():
    user = current_user
    form = NoteForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        attachment = request.files[form.attachment.name]
        if attachment:
            current_app.logger.debug(f'Attachment inside {attachment}')
            filename_prefix = str(uuid.uuid4())
            new_filename = filename_prefix + '.' + attachment.filename.split('.')[-1]
            path_to_file = DIR_PATH + new_filename
            attachment.save(path_to_file)
            note = Note(title=title, description=description, file_path=path_to_file, 
                        org_attachment_filename=attachment.filename, attachment_hash = new_filename, owner_id=user.id)
            db.session.add(note)
        else:
            note = Note(title=title, description=description, owner_id=user.id)
            db.session.add(note)
        db.session.commit()
        flash('Note added successfully')
        return redirect(request.url)
    return render_template("add_note.html", form=form)

@notes_bp.route('/private-notes/<string:file_hash>', methods=["GET", "POST"])
@login_required
def download_file_private(file_hash):
    file_to_download = Note.query.filter_by(attachment_hash=file_hash).first()
    if file_to_download:
        path_to_file = file_to_download.file_path
        org_filename = file_to_download.org_attachment_filename
        try:
            return send_file(path_to_file, attachment_filename = org_filename, as_attachment = True)
        except Exception as e:
            current_app.logger.debug(e)

@notes_bp.route('/public-notes/<string:file_hash>', methods=["GET", "POST"])
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


@notes_bp.route('/private-notes', methods=["GET", "POST"])
@login_required
def private_notes():
    private_notes = current_user.notes.order_by(Note.timestamp.desc()).all()
    return render_template("private_notes.html", private_notes = private_notes)

@notes_bp.route('/private-notes/make-public/<int:note_id>', methods=["GET", "POST"])
@login_required
def make_public(note_id):
    user = current_user
    note = Note.query.filter_by(id=note_id).first()
    if note.owner_id == user.id:
        note.is_public = True
        db.session.commit()
        flash('Note added to public notes.', category='info')
        return redirect(url_for('notes.private_notes'))   
    else:
        return redirect(url_for('dashboard.index'), 403)

@notes_bp.route('/private-notes/delete/<int:note_id>', methods=["GET", "DELETE", "OPTIONS"])
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

@notes_bp.route('/private-notes/files/delete/<int:note_id>', methods=['OPTIONS', 'DELETE'])
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

@notes_bp.route('/private-notes/files/<int:note_id>', methods=['OPTIONS', 'PATCH'])
@login_required
def upload_note_file(note_id):
    if request.method == 'PATCH':
        user = current_user
        note = Note.query.filter_by(id=note_id).first()
        if note.owner_id == user.id:
            note_file = request.files['Note']
            if(len(note_file.filename) > 0):
                filename_prefix = str(uuid.uuid4())
                new_filename = filename_prefix + '.' + note_file.filename.split('.')[-1]
                path_to_file = DIR_PATH + new_filename
                note_file.save(path_to_file)   
                note.attachment_hash = new_filename
                note.file_path = path_to_file
                note.org_attachment_filename = note_file.filename
                response = jsonify("File added")
                db.session.commit()
                flash('File uploaded successfully.', category='success')
            else:
                response = jsonify("Error: Empty content of file.")
        else:
            response = jsonify('Article not found')
    else:
        reponse = jsonify('Invalid method')
    return response

@notes_bp.route('/private-notes/make-private/<int:note_id>', methods=["GET", "POST"])
@login_required
def make_private(note_id):
    user=current_user
    note=Note.query.filter_by(id=note_id).first()
    if note.owner_id == user.id:
        note.is_public = False
        db.session.commit()
        flash('Note changed to private.', category='info')
        return redirect(url_for('notes.private_notes'))
    else:
        return redirect(url_for('dashboard.index'), 403)

@notes_bp.route('/private-notes/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    title = 'Edit note'
    note = Note.query.get_or_404(note_id)
    form = NoteForm(obj=note)
    if request.method == 'POST' and form.validate_on_submit():
        if form.attachment.data:
            attachment = request.files[form.attachment.name]
            if(len(attachment.filename) > 0):
                filename_prefix = str(uuid.uuid4())
                new_filename = filename_prefix + '.' + attachment.filename.split('.')[-1]
                path_to_file = DIR_PATH + new_filename
                attachment.save(path_to_file)   
                note.attachment_hash = new_filename
                note.file_path = path_to_file
                note.org_attachment_filename = attachment.filename
        note.title = form.title.data
        note.description = form.description.data
        db.session.commit()
        flash('Note edited successfully.', category='success')
        return redirect(url_for('notes.private_notes'))
    form.title.data = note.title
    form.description.data = note.description
    return render_template('edit_note.html', form=form, title=title, note=note)

@notes_bp.route('/subscribed-notes', methods=['GET'])
@login_required
def subscribed_notes():
    subscribed_notes = current_user.subscribed_notes
    return render_template('subscribed_notes.html', subscribed_notes=subscribed_notes)

@notes_bp.route('/public-notes/subscribe/<int:note_id>', methods=["GET", "POST"])
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

@notes_bp.route('/public-notes/unsubscribe/<int:note_id>', methods=["GET", "POST"])
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


@notes_bp.route('/public-notes', methods=["GET"])
def public_notes():
    notes = Note.query.filter_by(is_public=True).order_by(Note.timestamp.asc()).all()
    return render_template('public_notes.html', notes=notes)     