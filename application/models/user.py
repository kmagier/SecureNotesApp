from database import db
from flask import redirect, url_for
import bcrypt
from app import login_manager
from flask_login import UserMixin
# from flask_sqlalchemy import inspect


followed_notes = db.Table('followed_notes', 
                db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                db.Column('note_id', db.Integer, db.ForeignKey('notes.id'))
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), index=True, unique=True)
    email = db.Column(db.String(80), index=True, unique=True)
    password_hash = db.Column(db.String(256), index=False, unique=True)
    salt = db.Column(db.String(256))
    notes = db.relationship('Note', backref='owner', lazy='dynamic') 
    subscribed_notes = db.relationship('Note', secondary=followed_notes, backref=db.backref('followers', lazy='dynamic'))  

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())


def check_existing_user(user):
    existing_user = User.query.filter_by(username=user).first()
    if existing_user is not None:
        return True
    else:
        return False

@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    else:
        return None

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('auth.login'))
