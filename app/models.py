from app import db, login
from datetime import datetime
from flask_login import UserMixin
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash


# UserMixin is used to allow the class model to work with Flask-Login
class User(UserMixin, db.Model):  # SQLAlchemy class model must inherit
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # creates relationship between databases
    # requires the name of the Class model instead of the database table
    # backref='author' means that each post will have a field such as post.author
    # that references back to the user that posted the post
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """Uses werkzeug module to generate secure password hash
        and sets it for the user"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Uses werkzeug module to check the given password
        against the hash"""
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)


# required to load users that are already logged in without having to log in again
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # ForeignKey('table.field') is used to create links between database tables

    def __repr__(self):
        return '<Post {}>'.format(self.body)
