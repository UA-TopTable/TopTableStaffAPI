import os
from socket import SocketIO
from flask import Flask,jsonify, redirect, request, session
from flask_mail import Mail
from flask_restx import Api

from apis import blueprint,api
from secret import FLASK_SECRET_KEY

from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__)
    api.init_app(app)

    app.secret_key=FLASK_SECRET_KEY

    socketio=SocketIO(app)


    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'

    mail = Mail(app)

    return app,socketio,mail


app,socketio,mail=create_app()

if __name__ == "__main__":
    socketio.run(create_app())