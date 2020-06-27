from flask import Flask, Blueprint, current_app, request, url_for, redirect, render_template, jsonify
from database import db
from forms.forms import NoteForm
from models.user import User
from flask_login import login_required, current_user
# from routes.auth.auth import get_username
from models.note import Note


notes_bp = Blueprint('notes', __name__)

@notes_bp.route('/add-note', methods=["GET", "POST"])
@login_required
def add_note():
    user = current_user
    form = NoteForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        note = Note(title=title, description=description, owner_id=user.id)
        db.session.add(note)
        db.session.commit()
        current_app.logger.debug("Note added")
        current_app.logger.debug(f"Content: {description}")
        return redirect(request.url)
    return render_template("add-note.html", form=form)

@notes_bp.route('/private-notes', methods=["GET", "POST"])
@login_required
def private_notes():
    privateNotes = []
    user = current_user
    notes = user.notes.all()
    for note in notes: 
        current_app.logger.debug(note)
        privateNotes.append(note)
    return render_template("private-notes.html", notes = privateNotes)

@notes_bp.route('/private-notes/make-public/<int:note_id>', methods=["GET", "POST"])
@login_required
def make_public(note_id):
    user=current_user
    note=Note.query.filter_by(id=note_id).first()
    if note.owner_id == user.id:
        note.is_public = True
        db.session.commit()
        return redirect(url_for('notes.private_notes'))   
    else:
        return redirect(url_for('dashboard.index'), 403)

@notes_bp.route('/private-notes/delete/<int:note_id>', methods=["GET", "DELETE", "OPTIONS"])
@login_required
def delete_note(note_id):
    if request.method == 'DELETE':
        user=current_user
        note=Note.query.filter_by(id=note_id).first()
        if note.owner_id == user.id:
            db.session.delete(note)
            db.session.commit()
            response = jsonify('Note deleted')   
        else:
            response = jsonify("You don't have permission to delete this note.")
    else:
        response = jsonify('Invalid method')
    return response

@notes_bp.route('/private-notes/make-private/<int:note_id>', methods=["GET", "POST"])
@login_required
def make_private(note_id):
    user=current_user
    note=Note.query.filter_by(id=note_id).first()
    if note.owner_id == user.id:
        note.is_public = False
        db.session.commit()
        return redirect(url_for('notes.private_notes'))
    else:
        return redirect(url_for('dashboard.index'), 403)

@notes_bp.route('/public-notes', methods=["GET"])
def public_notes():
    public_notes = []
    notes = Note.query.filter_by(is_public=True).all()
    for note in notes:
        public_notes.append(note)
    return render_template('public-notes.html', notes=public_notes)     