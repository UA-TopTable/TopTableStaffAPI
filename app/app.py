import os
import boto3
from flask import Flask,jsonify, redirect, request, session
from flask_restx import Api

from apis import blueprint,api
from secret import FLASK_SECRET_KEY

def create_app():
    app = Flask(__name__)
    api.init_app(app)

    app.secret_key=FLASK_SECRET_KEY

    return app