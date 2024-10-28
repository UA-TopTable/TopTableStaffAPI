import os
import boto3
from flask import current_app, jsonify, request
from flask_restx import Namespace,Resource,fields
from services.auth_service import confirm_sign_up, login, sign_out, sign_up

api=Namespace("auth",description="Authentication operations")

new_request_metadata_model=api.model("new_request_metadata",{
    "DeviceKey":fields.String,
    "DeviceGroupKey":fields.String
})

login_response_model=api.model("login_response",{
    "AccessToken":fields.String(),
    "ExpiresIn":fields.Integer(),
    "TokenType":fields.String(),
    "RefreshToken":fields.String(),
    "IdToken":fields.String(),
    "NewDeviceMetadata":fields.Nested(new_request_metadata_model)
})

@api.route("/log_in")
class Login(Resource):
    @api.doc('login')
    @api.expect({
        "email":fields.String(required=True),
        "password":fields.String(required=True)
    },validate=True)
    @api.param("email",_in="body")
    @api.param("password",_in="body")
    @api.response(200,description="success",model=login_response_model)
    @api.response(400,"wrong response body")
    @api.response(401,"wrong email/password")
    def post(self):
        try:
            data=request.json
            email=data.get("email")
            password=data.get("password")

            response,status_code=login(email,password)
            if status_code==200:
                return jsonify(response.get("AuthenticationResult"),200)
            else:
                return response,status_code
        except KeyError:
            return "Incorrect input",400
        
@api.route("/sign_up")
class SignUp(Resource):
    @api.doc("sign up")
    @api.expect({
        "email":fields.String(required=True),
        "password":fields.String(required=True),
        "name":fields.String(required=True),
        "phone_number":fields.String(required=True)
    },validate=True)
    @api.response(201,"user created")
    @api.response(400,"wrong body")
    @api.response(409,"username already exists")
    def post(self):
        try:
            data=request.json
            email=data.get("email")
            password=data.get("password")
            name=data.get("name")
            phone_number=data.get("phone_number")

            return sign_up(email,password,name,phone_number)
        except KeyError:
            return "Wrong Body",400
        
@api.route("/sign_up/confirm")
class ConfirmSignUp(Resource):
    @api.doc("confirm sign up")
    @api.expect({
        "email":fields.String(required=True),
        "confirmation_code":fields.String(required=True)
    },validate=True)
    @api.response(200,"user confirmed")
    @api.response(400,"wrong body")
    @api.response(400,"wrong confirmation code")
    @api.response(410,"confirmation code expired")
    def post(self):
        try:
            data=request.json
            email=data.get("email")
            confirmation_code=data.get("confirmation_code")
            return confirm_sign_up(email,confirmation_code)
        except KeyError:
            return "Wrong body",400
        
        
@api.route("/sign_out")
class SignOut(Resource):
    @api.doc("sign out")
    @api.expect({
        "access_token":fields.String(required=True)
    },validate=True)
    @api.response(200,"sign out successful")
    @api.response(400,"Wrong body")
    @api.response(401,"invalid access token")
    def post(self):
        try:
            data=request.json
            access_token=data.get("access_token")
            return sign_out(access_token)
        except KeyError:
            return "Wrong body",400