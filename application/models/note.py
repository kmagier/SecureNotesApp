from database import db

class privateNote:
    def __init__(self, noteID, owner, content, isPublic = None):
        self.noteID = noteID
        self.owner = owner
        self.content = content
        self.isPublic = isPublic if isPublic is not None else False


class publicNote:
    def __init__(self, owner, content):
        self.owner = owner
        self.content = content

def AddNote(owner, content, isPublic):
    noteID = str(db.incr("NOTE_COUNTER"))
    db.hset("note:" + noteID, "ID", noteID)
    db.hset("note:" + noteID, "Owner", owner)
    db.hset("note:" + noteID, "Content", content)
    db.hset("note:" + noteID, "isPublic", str(isPublic))
    db.lpush("notes:" + owner, noteID)