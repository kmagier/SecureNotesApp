from datetime import datetime
from application.models.user import User, subscribed_notes
from application import db
from flask import current_app
import os
import uuid

class Note(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), index=True)
    description = db.Column(db.String(255), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    org_attachment_filename = db.Column(db.String(256), index=True)
    attachment_hash = db.Column(db.String(80), index=True, unique=True, nullable=True)
    file_path = db.Column(db.String(256), index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_public = db.Column(db.Boolean, unique=False, default=False) 


    def edit_note(self, title=None, description=None, attachment=None):
        current_app.logger.debug("inside edit_note of Note")
        self.title = title
        self.description = description
        if attachment:
            current_app.logger.debug("inside edit_note of Note and attachment")
            self.upload_attachment(attachment)
        db.session.commit()
            

    def upload_attachment(self, attachment):
        if len(attachment.filename) > 0:
            filename_prefix = str(uuid.uuid4())
            new_filename = filename_prefix + '.' + attachment.filename.split('.')[-1]
            path_to_file = os.path.join(current_app.static_folder, 'files', new_filename)
            attachment.save(path_to_file)   
            self.attachment_hash = new_filename
            self.file_path = path_to_file
            self.org_attachment_filename = attachment.filename
            db.session.commit()
        else:
            return False

    def is_subscribing(self, user): 
        return self.subscribers.filter(subscribed_notes.c.user_id == user.id).count() > 0 

    def subscribe_note(self, user):
        if not self.is_subscribing(user):
            self.subscribers.append(user)
    
    def unsubscribe_note(self, user):
        if self.is_subscribing(user):
            self.subscribers.remove(user)

    def __repr__(self):
        return f'<Note id: {self.id}>'
    
    def serialize(self):
        return {"id": self.id,
                "author": self.author,
                "title": self.title,
                "description": self.description,
                "file": self.file_path}


