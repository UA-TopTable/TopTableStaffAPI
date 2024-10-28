import os
import boto3
from flask import current_app


cognito=boto3.client('cognito-idp',os.environ["AWS_REGION"])

def login(email,password):
    try:
        response=cognito.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME":email,
                    "PASSWORD":password
                },
                ClientId=current_app.config["AWS_COGNITO_USER_POOL_CLIENT_ID"]
        )

        return response,200
    except cognito.exceptions.NotAuthorizedException:
        return "Wrong username/password",401
    
def sign_up(email,password,name,phone_number):
    try:
        cognito.sign_up(
            ClientId=current_app.config["AWS_COGNITO_USER_POOL_CLIENT_ID"],
            Username=email,
            Password=password,
            UserAttributes=[
                {
                    "Name": "name",
                    "Value":name
                },
                {
                    "Name": "phone_number",
                    "Value":phone_number
                }
            ]
        )
        return "User created. Confirm registration via email",200
    except cognito.exceptions.UsernameExistsException:
        return "Username already exists",409
    
def confirm_sign_up(email,confirmation_code):
    try:
        cognito.confirm_sign_up(
            ClientId=current_app.config["AWS_COGNITO_USER_POOL_CLIENT_ID"],
            Username=email,
            ConfirmationCode=confirmation_code
        )
        return "user confirmed",200
    except cognito.exceptions.CodeMismatchException:
        return "Wrong confirmation code",400
    except cognito.exceptions.ExpiredCodeException:
        return "Confirmation code expired",410
    
def sign_out(access_token):
    try:
        cognito.global_sign_out(AccessToken=access_token)
        return "signed out successful",200
    except cognito.exceptions.NotAuthorizedException:
        return "Invalid access token",401