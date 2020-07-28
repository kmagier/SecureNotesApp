from datetime import datetime
from application.models.user import User, subscribed_notes
from application import db
from flask_sqlalchemy import inspect

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


