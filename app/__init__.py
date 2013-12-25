from flask import Flask
from flask.ext import restful
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
restApi = restful.Api(app)
db = SQLAlchemy(app)

from api.api import WalletList, Users, Login, WalletItem, WalletUsers, Event
restApi.add_resource(WalletList, '/wallets')
restApi.add_resource(WalletItem, '/wallets/<int:wallet_id>')
restApi.add_resource(WalletUsers, '/wallets/<int:wallet_id>/users')
restApi.add_resource(Users, '/users')
restApi.add_resource(Login, '/login')
restApi.add_resource(Event, '/wallets/<int:wallet_id>/events')
