from datetime import datetime
from models.user import User
from database import db
from flask_sqlalchemy import inspect

class Note(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), index=True)
    description = db.Column(db.String(255), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    org_attachment_filename = db.Column(db.String(256), index=True)
    attachment_hash = db.Column(db.String(80), index=True, unique=True)
    file_path = db.Column(db.String(256), index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_public = db.Column(db.Boolean, unique=False, default=False) 

    def __repr__(self):
        return f'<Article id: {self.id}>'
    
    def serialize(self):
        return {"id": self.id,
                "author": self.author,
                "title": self.title,
                "description": self.description,
                "file": self.file_path}



# class privateNote:
#     def __init__(self, noteID, owner, content, isPublic = None):
#         self.noteID = noteID
#         self.owner = owner
#         self.content = content
#         self.isPublic = isPublic if isPublic is not None else False


# class publicNote:
#     def __init__(self, owner, content):
#         self.owner = owner
#         self.content = content

# def AddNote(owner, content, isPublic):
#     noteID = str(db.incr("NOTE_COUNTER"))
#     db.hset("note:" + noteID, "ID", noteID)
#     db.hset("note:" + noteID, "Owner", owner)
#     db.hset("note:" + noteID, "Content", content)
#     db.hset("note:" + noteID, "isPublic", str(isPublic))
#     db.lpush("notes:" + owner, noteID)