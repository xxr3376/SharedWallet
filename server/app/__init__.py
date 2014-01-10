from flask import Flask, send_from_directory, redirect
from flask.ext import restful
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
restApi = restful.Api(app)
db = SQLAlchemy(app)

@app.route('/frontend/<path:filename>')
def frontend(filename):
    return send_from_directory('frontend/', filename)
@app.route('/')
def index():
    return redirect('/static/frontend/index.html')

from api.api import WalletList, Users, Login, WalletItem, WalletUsers, Event, EventList
restApi.add_resource(WalletList, '/wallets')
restApi.add_resource(WalletItem, '/wallets/<int:wallet_id>')
restApi.add_resource(WalletUsers, '/wallets/<int:wallet_id>/users')
restApi.add_resource(Users, '/users')
restApi.add_resource(Login, '/login')
restApi.add_resource(EventList, '/wallets/<int:wallet_id>/events')
restApi.add_resource(Event, '/wallets/<int:wallet_id>/events/<int:event_id>')

