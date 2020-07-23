from database import db
from datetime import datetime
from pytz import timezone
from flask import redirect, url_for
import bcrypt
from app import login_manager
from flask_login import UserMixin
# from flask_sqlalchemy import inspect


subscribed_notes = db.Table('subscribed_notes', 
                db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                db.Column('note_id', db.Integer, db.ForeignKey('notes.id'))
)

followers = db.Table('followers',
            db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
            db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
            )

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), index=True, unique=True)
    email = db.Column(db.String(80), index=True, unique=True)
    password_hash = db.Column(db.String(256), index=False, unique=True)
    salt = db.Column(db.String(256)) 
    about_me = db.Column(db.String(300))
    registered_date = db.Column(db.DateTime, default=datetime.now())
    last_seen = db.Column(db.DateTime, default=datetime.now())
    notes = db.relationship('Note', backref='owner', lazy='dynamic') 
    subscribed_notes = db.relationship('Note', secondary=subscribed_notes, backref=db.backref('subscribers', lazy='dynamic'))  
    followed = db.relationship('User', secondary=followers, primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.followed_id == id),
                                backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    is_admin = db.Column(db.Boolean, unique=False, default=False)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0


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
