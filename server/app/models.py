from app import db
import hashlib
import random
import uuid
import datetime
from flask import abort


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    token = db.Column(db.String(64), index=True)
    token_expire_time = db.Column(db.DateTime)
    wallets = db.relationship('Wallet', backref='user', lazy='dynamic')
    wallet_users = db.relationship('WalletUser', backref='user', lazy='dynamic')
    wallet_events = db.relationship('MoneyEvent', backref='user', lazy='dynamic')
    wallet_events = db.relationship('MoneyTransaction', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        if 'password' in kwargs:
            raw = kwargs.pop('password')
            self.password = self.create_password(raw)
        if 'username' in kwargs:
            username = kwargs.pop('username')
            self.username = username.lower()
        for k, v in kwargs.items():
            setattr(self, k, v)
    def update_token(self):
        self.token = uuid.uuid1().hex
        self.token_expire_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=10000)
        return self.token
    def check_password(self, raw):
        if not self.password:
            return False
        if '$' not in self.password:
            return False
        salt, hsh = self.password.split('$')
        passwd = '%s%s%s' % (salt, raw, db.app.config['PASSWORD_SECRET'])
        verify = hashlib.sha1(passwd).hexdigest()
        return verify == hsh
    @classmethod
    def get_by_token(cls, token):
        user = cls.query.filter_by(token=token).first()
        if user and user.token_expire_time > datetime.datetime.utcnow():
            return user
        abort(401)
    @staticmethod
    def create_password(raw):
        salt = User.create_token(8)
        passwd = '%s%s%s' % (salt, raw, db.app.config['PASSWORD_SECRET'])
        hsh = hashlib.sha1(passwd).hexdigest()
        return "%s$%s" % (salt, hsh)
    @staticmethod
    def create_token(length=16):
        chars = ('0123456789'
                    'abcdefghijklmnopqrstuvwxyz'
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        salt = ''.join([random.choice(chars) for i in range(length)])
        return salt

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)

    users = db.relationship('WalletUser', backref='wallet', lazy='dynamic')
    events = db.relationship('MoneyEvent', backref='wallet', lazy='dynamic')

class WalletUser(db.Model):
    NORMAL, ADMIN = range(1, 3)
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ballance = db.Column(db.Float)
    role = db.Column(db.Integer)

class MoneyEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    author = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)

    transactions = db.relationship('MoneyTransaction', backref='event', lazy='dynamic')

class MoneyTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('money_event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float)
    notes = db.Column(db.Text)
