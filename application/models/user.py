from application import db, login
from datetime import datetime
from flask import redirect, url_for, current_app, request
import bcrypt
from time import time
from flask_login import UserMixin
import jwt
import uuid



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
    avatar = db.Column(db.String(256), index=False, unique=False, nullable=True)
    about_me = db.Column(db.String(300))
    registered_date = db.Column(db.DateTime, default=datetime.now())
    last_seen = db.Column(db.DateTime, default=datetime.now())
    notes = db.relationship('Note', backref='owner', lazy='dynamic') 
    subscribed_notes = db.relationship('Note', secondary=subscribed_notes, backref=db.backref('subscribers', lazy='dynamic'))  
    followed = db.relationship('User', secondary=followers, primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.followed_id == id),
                                backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    is_admin = db.Column(db.Boolean, unique=False, default=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def get_reset_password_token(self, expires_in=300):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
        current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

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

@login.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    else:
        return None

@login.unauthorized_handler
def unauthorized():
    return redirect(url_for('auth.login'))
