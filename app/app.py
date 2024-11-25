from socket import SocketIO
from flask import Flask,jsonify, redirect, request, session
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

    return app,socketio

app,socketio=create_app()

if __name__ == "__main__":
    socketio.run(create_app())