from flask import Flask, Blueprint, current_app, request, url_for, redirect, render_template
from database import db
from forms.forms import NoteForm
from routes.auth.auth import get_username
from models.note import *

notes_bp = Blueprint('notes', __name__)

@notes_bp.route('/add-note', methods=["GET", "POST"])
def add_note():
    session_id = request.cookies.get('session_id', '')
    username = get_username(session_id)
    form = NoteForm(request.form)
    if not username or username=='None':
        return redirect(url_for('auth.login'))
    if request.method == "POST" and form.validate_on_submit():
        content = form.note.data
        AddNote(username, content, False)
        current_app.logger.debug("Note added")
        current_app.logger.debug("Content: %s" % content)
        return redirect(request.url)
    return render_template("add-note.html", form=form)

@notes_bp.route('/private-notes', methods=["GET", "POST"])
def private_notes():
    privateNotes = []
    session_id = request.cookies.get('session_id', '')
    username = get_username(session_id)
    if not username or username=='None':
        return redirect(url_for('auth.login'))
    notes_id = db.lrange("notes:" + username, 0, -1)
    for id in notes_id:
        note_id = db.hget("note:" + id, "ID")
        owner = db.hget("note:" + id, "Owner")
        content = db.hget("note:" + id, "Content")
        isPublic = db.hget("note:" + id, "isPublic")
        note = privateNote(note_id, owner, content, isPublic)
        privateNotes.append(note)
    return render_template("private-notes.html", notes = privateNotes)

@notes_bp.route('/private-notes/<int:note_id>', methods=["GET", "POST"])
def make_public(note_id):
    session_id = request.cookies.get('session_id', '')
    username = get_username(session_id)
    if not username or username=='None':
        return redirect(url_for('auth.login'))
    if str(note_id) in db.lrange("Public notes", 0, -1):
        flash("Note is already public")
        return redirect(url_for('notes.private_notes'))
    else:
        owner = db.hget("note:" + str(note_id), "Owner")
        current_app.logger.debug("Username: %s" % username)
        current_app.logger.debug("Owner: %s" % owner)
        if owner == username:
            db.lpush("Public notes", str(note_id))
            db.hset("note:" + str(note_id), "isPublic", "True")
            current_app.logger.debug("Dodawanie publicznych notatek dziala")
            current_app.logger.debug(db.lrange("Public notes", 0, -1))
        else:
            flash("Nie jestes wlascicielem notatki")
            return redirect(url_for('dashboard.index'), 403)
    return redirect(url_for('notes.private_notes'))   

@notes_bp.route('/public-notes', methods=["GET"])
def public_notes():
    public_notes = []
    public_notes_ids = db.lrange("Public notes", 0, -1)
    for id in public_notes_ids: 
        public_note_owner = db.hget("note:" + id, "Owner")
        public_note_content = db.hget("note:" + id, "Content")
        public_note = publicNote(public_note_owner, public_note_content)
        public_notes.append(public_note)
    return render_template('public-notes.html', notes=public_notes)     