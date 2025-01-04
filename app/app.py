import os
import threading
from flask_socketio import SocketIO
from flask import Flask,jsonify, redirect, request, session
from flask_mail import Mail
from flask_restx import Api

from secret import FLASK_SECRET_KEY, ROOT_PATH_PREFIX
from apis import blueprint,api

from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__, static_url_path=f'/{ROOT_PATH_PREFIX}/static')
    api.init_app(app)

    app.secret_key=FLASK_SECRET_KEY


    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

    return app


app=create_app()
mail=Mail(app)
socketio = SocketIO(app,path=f'{ROOT_PATH_PREFIX}/socket.io')

if __name__ == "__main__":
    socketio.run(app)

#Do not remove. This ensures that the socket parts are properly loaded when the app is run (that's just how flask/python is)
from apis.events import *
