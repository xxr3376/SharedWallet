#! encoding=utf-8
from flask.ext import restful
from flask.ext.restful import fields, marshal_with
from flask import request, abort
from app import db
from app.models import User, Wallet, WalletUser, MoneyEvent, MoneyTransaction
from flask.ext.restful import reqparse
from datetime import datetime
from flask.ext.restful.utils import cors

class WalletList(restful.Resource):
    token_parser = reqparse.RequestParser()
    token_parser.add_argument('token', type=str, required=True, location='args')

    create_parse = reqparse.RequestParser()
    create_parse.add_argument('token', type=str, required=True, location='args')
    create_parse.add_argument('name', required=True)
    create_parse.add_argument('description', required=True)
    def get(self):
        args = self.__class__.token_parser.parse_args()
        user = User.get_by_token(args['token'].strip())
        wu_list = WalletUser.query.filter_by(user_id=user.id).all()
        result = []
        for wu in wu_list:
            wallet = wu.wallet
            row = {'id': wallet.id, 'name': wallet.name, 'description': wallet.description,\
                'timestamp': wallet.timestamp.isoformat(), 'user_id': wallet.create_by }
            result.append(row)
        return result, 200,\
            { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods' : '*' }
    def post(self):
        args = self.__class__.create_parse.parse_args()
        user = User.get_by_token(request.args['token'].strip())
        new_wallet = Wallet(name=args['name'].strip(), description=args['description'].strip(),\
                create_by=user.id, timestamp=datetime.utcnow())
        db.session.add(new_wallet)
        db.session.commit()
        db.session.add(WalletUser(wallet_id=new_wallet.id, user_id=user.id, role=WalletUser.ADMIN, ballance=0.0))
        db.session.commit()
        return {'id': new_wallet.id}, 201
    def options (self):
        return {'Allow' : 'POST' }, 200, \
        { 'Access-Control-Allow-Origin': '*', \
        'Access-Control-Allow-Methods' : 'POST,GET',\
        'Content-Type' : 'application/json'}

class WalletItem(restful.Resource):
    token_parser = reqparse.RequestParser()
    token_parser.add_argument('token', type=str, required=True)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('token', type=str, required=True)
    put_parser.add_argument('name')
    put_parser.add_argument('description')

    def get(self, wallet_id):
        args = self.__class__.token_parser.parse_args()
        user = User.get_by_token(args['token'].strip())
        wallet = Wallet.query.get_or_404(wallet_id)
        wallet.users.filter_by(user_id=user.id).first_or_404()
        return {'id': wallet.id, 'name': wallet.name, \
                'description': wallet.description, 'timestamp': wallet.timestamp.isoformat()}
    def put(self, wallet_id):
        args = self.__class__.token_parser.parse_args()
        user = User.get_by_token(args['token'].strip())
        wallet = Wallet.query.get_or_404(wallet_id)
        wallet_user = wallet.users.filter_by(user_id=user.id).first_or_404()
        if wallet_user.role != WalletUser.ADMIN:
            abort(403)
        if 'name' in args:
            wallet.name = args['name']
        if 'description' in args:
            wallet.description = args['description']
        db.session.commit()
        return {'status': 'SUCCESS'}, 200

class WalletUsers(restful.Resource):
    token_parser = reqparse.RequestParser()
    token_parser.add_argument('token', type=str, required=True)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('token', type=str, required=True, location="args")
    post_parser.add_argument('user_id', type=int, required=True)
    post_parser.add_argument('role', type=str, default='normal')

    delete_parser= reqparse.RequestParser()
    delete_parser.add_argument('token', type=str, required=True, location="args")
    delete_parser.add_argument('user_id', type=int, required=True)
    def get(self, wallet_id):
        args = self.__class__.token_parser.parse_args()
        user = User.get_by_token(args['token'].strip())
        wallet = Wallet.query.get_or_404(wallet_id)
        wallet.users.filter_by(user_id=user.id).first_or_404()
        return map(lambda x: \
                {'id': x.user_id, \
                'name': x.user.name, 'ballance': x.ballance, 'role': x.role}, \
                wallet.users.all())
    def post(self, wallet_id):
        args = self.__class__.post_parser.parse_args()
        user = User.get_by_token(request.args['token'].strip())
        wallet = Wallet.query.get_or_404(wallet_id)
        wallet_user = wallet.users.filter_by(user_id=user.id).first_or_404()
        if wallet_user.role != WalletUser.ADMIN:
            abort(403)
        target_user = wallet.users.filter_by(user_id=args['user_id']).first()
        if args['role'] not in ['admin', 'normal']:
            abort(400)
        if not target_user:
            new_user = User.query.get_or_404(args['user_id'])
            target_user = WalletUser(wallet_id=wallet.id, user_id=new_user.id, role=WalletUser.NORMAL)
            target_user.role = WalletUser.ADMIN if args['role'] == 'admin' else WalletUser.NORMAL
            target_user.ballance = 0.0
            db.session.add(target_user)
            db.session.commit()
            return {'status': 'SUCCESS'}, 200
        return {'status': 'already exist'}, 409
    def put(self, wallet_id):
        args = self.__class__.post_parser.parse_args()
        user = User.get_by_token(request.args['token'].strip())
        wallet = Wallet.query.get_or_404(wallet_id)
        wallet_user = wallet.users.filter_by(user_id=user.id).first_or_404()
        if wallet_user.role != WalletUser.ADMIN:
            abort(403)
        target_user = wallet.users.filter_by(user_id=args['user_id']).first()
        if target_user.user_id == user.id:
            abort(400)
        if args['role'] not in ['admin', 'normal']:
            abort(400)
        target_user.role = WalletUser.ADMIN if args['role'] == 'admin' else WalletUser.NORMAL
        db.session.commit()
        return {'status': 'SUCCESS'}, 200
    def delete(self, wallet_id):
        args = self.__class__.post_parser.parse_args()
        user = User.get_by_token(args['token'].strip())
        wallet = Wallet.query.get_or_404(wallet_id)
        wallet_user = wallet.users.filter_by(user_id=user.id).first_or_404()
        if wallet_user.role != WalletUser.ADMIN:
            abort(403)
        target_user = wallet.users.filter_by(user_id=args['user_id']).first_or_404()
        if target_user.user_id == user.id:
            abort(400)
        if target_user.ballance < 0.01:
            db.session.delete(target_user)
            db.session.commit()
            return {'status': 'SUCCESS'}, 200
        else:
            return {'status': 'still has money'}, 400


class Users(restful.Resource):
    new_user_parser = reqparse.RequestParser()
    new_user_parser.add_argument('username', type=str, required=True)
    new_user_parser.add_argument('password', type=str, required=True)
    new_user_parser.add_argument('name', required=True)

    update_user_parser = reqparse.RequestParser()
    update_user_parser.add_argument('token', type=str, required=True, location="args")
    update_user_parser.add_argument('password', type=str)
    update_user_parser.add_argument('name')
    def get(self):
        users = User.query.all()
        return map(lambda u: {'id': u.id, 'name': u.name}, users)
    def post(self):
        args = self.__class__.new_user_parser.parse_args()
        try:
            user = User(username=args['username'],password=args['password'],name=args['name'])
            db.session.add(user)
            db.session.commit()
        except:
            return {'status': 'username exist'}, 409
        return {'id' : user.id}, 201
    def put(self):
        args = self.__class__.update_user_parser.parse_args()
        user = User.get_by_token(request.args['token'])
        if args.get('password', None):
            user.password = User.create_password(args['password'].strip())
        if args.get('name', None):
            user.name = args['name'].strip()
        db.session.commit()
        return {'status': 'SUCCESS'}, 200

class EventList(restful.Resource):
    token_parser = reqparse.RequestParser()
    token_parser.add_argument('token', type=str, required=True, location='args')
    event_parser = reqparse.RequestParser()
    token_parser.add_argument('token', type=str, required=True, location='args')
    event_parser.add_argument('name', required=True)
    event_parser.add_argument('description')
    event_parser.add_argument('transaction', type=list, required=True)
    def get(self, wallet_id):
        args = self.__class__.token_parser.parse_args()
        user = User.get_by_token(args['token'].strip())
        wallet = Wallet.query.get_or_404(wallet_id)
        wallet.users.filter_by(user_id=user.id).first_or_404()
        return map(lambda x: \
                {'id': x.id, 'user_id': x.author, \
                'name': x.name, 'description': x.description, 'timestamp': x.timestamp.isoformat()}, \
                wallet.events.all())
    def post(self, wallet_id):
        args = self.__class__.event_parser.parse_args()
        user = User.get_by_token(request.args['token'].strip())
        wallet = Wallet.query.get_or_404(wallet_id)
        wallet_user = wallet.users.filter_by(user_id=user.id).first_or_404()
        if wallet_user.role != WalletUser.ADMIN:
            abort(403)
        total = 0.0
        for line in args['transaction']:
            user_id = int(line['user_id'])
            total += float(line['amount'])
            if wallet.users.filter_by(user_id=user_id).count() == 0:
                return {'status': 'user not exist'}, 400
        if abs(total) > 0.01:
            return {'status': 'total money is not right'}, 400
        event = MoneyEvent(wallet_id=wallet.id, author=user.id, name=args['name'],\
               description=args['description'], timestamp=datetime.utcnow())
        db.session.add(event)
        db.session.commit()
        for line in args['transaction']:
            transaction = MoneyTransaction(event_id=event.id, \
                    user_id=int(line['user_id']), amount=float(line['amount']), \
                    notes = line.get('notes', ''))
            db.session.add(transaction)
            wu = wallet.users.filter_by(user_id=int(line['user_id'])).first()
            wu.ballance += line['amount']
        db.session.commit()
        return {'id': event.id}, 201
class Event(restful.Resource):
    token_parser = reqparse.RequestParser()
    token_parser.add_argument('token', type=str, required=True)
    def get(self, wallet_id, event_id):
        args = self.__class__.token_parser.parse_args()
        user = User.get_by_token(args['token'].strip())
        wallet = Wallet.query.get_or_404(wallet_id)
        wallet.users.filter_by(user_id=user.id).first_or_404()
        event = MoneyEvent.query.get_or_404(event_id)
        result = {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "user_id": event.author,
            "transaction": [],
        }
        for transaction in event.transactions.all():
            tmp = {
                'user_id': transaction.user_id,
                'amount': transaction.amount,
                'notes': transaction.notes,
                'name': transaction.user.name
            }
            result['transaction'].append(tmp)
        return result
class Login(restful.Resource):
    def get(self):
        username = request.args.get('username', '')
        password = request.args.get('password', '')
        user = User.query.filter_by(username=username).first()
        if not user:
            return {'status': 'user not exist'}, 401, \
                { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods' : '*' }
        if user.check_password(password):
            user.update_token()
            db.session.commit()
            result = {'status': 'SUCCESS',
                    'token': user.token,
                    'user_id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'expire_time': user.token_expire_time.isoformat()
                }
            return result, 200, \
                { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods' : '*' }
        else:
            return {'status': 'password not correct'}, 401, \
                { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods' : '*' }
