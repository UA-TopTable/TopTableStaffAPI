import boto3
from flask_restx import Namespace, Resource, fields, Api
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from flask import Flask, request, jsonify, redirect
from werkzeug.utils import secure_filename
from data.db_engine import DATABASE_URL
from services.db_service import add_picture, modify_description, add_working_hours, get_working_hours, modify_working_hours, delete_picture, get_restaurant_by_owner
from services.auth_service import get_user
from datetime import datetime
from string import ascii_letters, digits
from random import choice
from os.path import splitext
from secret import S3_BUCKET


AWS_REGION="us-east-1"

api=Namespace("upload", path="/api/v1/upload", description="Operations to upload pictures and description of the restaurant")

s3_client = boto3.client('s3', region_name=AWS_REGION)

def generate_random_string(length):
    # choose from all lowercase letter
    letters = ascii_letters + digits
    result_str = ''.join(choice(letters) for i in range(length))
    return result_str

@api.route('/upload_picture/<int:restaurant_id>')
class ImageUpload(Resource):
    @api.doc("upload a picture")
    @api.expect({
        "file":fields.Raw(required=True)
    })
    @api.response(200,"File successfully uploaded")
    @api.response(400,"Invalid file name")
    @api.response(400,"No file found in the request")
    def post(self, restaurant_id):
        """Upload a picture to S3"""
        if 'files[]' not in request.files:
            return {"message": "No file found in the request"}, 400
        
        
        files = request.files.getlist('files[]')
        uploaded_url = []
        try :
            if 'x-amzn-oidc-accesstoken' in request.headers:
                access_token = request.headers.get('x-amzn-oidc-accesstoken')
            elif "access_token" in request.cookies:
                access_token=request.cookies.get("access_token")
            else:
                return "You are not logged in", 403
            
            user=get_user(access_token)
            if user is None:
                return "You are not logged in", 403
            restaurants = get_restaurant_by_owner(user.get('id'))
            if restaurants is None or int(restaurant_id) not in [restaurant.get('id') for restaurant in restaurants]:
                return "You are not the owner of this restaurant", 403
        except : 
            return  'Error checking for the authentication of the user', 500

        for file in files :
            if file.filename == '':
                return {"message": "Invalid file name"}, 400
            
            _, extension = splitext(file.filename)
            filename = generate_random_string(32) + extension

            if filename == '':
                return {"message": "Invalid file name"}, 400
            
            filename = secure_filename(filename)

            try:
                # Upload de l'image à S3
                s3_client.upload_fileobj(
                    file,
                    S3_BUCKET,
                    filename
                )

                file_url = f"https://{S3_BUCKET}.s3.{S3_BUCKET}.amazonaws.com/{filename}"
                uploaded_url.append(file_url)
                #Fill in the DB with the new image
                add_picture(file_url, restaurant_id)

            except (NoCredentialsError, PartialCredentialsError):
                return {"message": "Missing credentials"}, 500
            except Exception as e:
                return {"message": str(e)}, 500
        return {"message": "Files successfully uploaded", "files_url": file_url, "restaurant_id": restaurant_id}, 200


@api.route('/upload_description/<int:restaurant_id>')
class DescriptionUpload(Resource):
    @api.doc("upload a description")
    @api.expect({
        "description":fields.String(required=True)
    })
    @api.response(200,"Description successfully modified")
    @api.response(400,"No description given")
    @api.response(500,"No restaurant found")
    def post(self,restaurant_id):
        description = request.form.get('description')
        if not description : 
            return {"message": "No description given"}, 400
        try:

            if 'x-amzn-oidc-accesstoken' in request.headers:
                access_token = request.headers.get('x-amzn-oidc-accesstoken')
            elif "access_token" in request.cookies:
                access_token=request.cookies.get("access_token")
            else:
                return "You are not logged in", 403
            
            user=get_user(access_token)
            if user is None:
                return "You are not logged in", 403
            restaurants = get_restaurant_by_owner(user.get('id'))
            if restaurants is None or int(restaurant_id) not in [restaurant.get('id') for restaurant in restaurants]:
                return "You are not the owner of this restaurant", 403

            #Modify the DB with the new description
            returnedValue = modify_description(description, restaurant_id)
            if returnedValue is None :
                return {"message" : "No restaurant found"}, 500
            elif returnedValue == '' :
                return {"message" : "No restaurant found"}, 500
            return {"message": "Description successfully modified", "description":description, "restaurant_id": restaurant_id}, 200
        except Exception as e:
            return {"message": str(e)}, 500


@api.route('/upload_working_hours/<int:restaurant_id>')
class WorkingHoursUpload(Resource):
    @api.doc("upload working hours")
    @api.expect({
        "day":fields.String(required=True),
        "opening_time":fields.DateTime(required=True),
        "closing_time":fields.DateTime(required=True)
    })
    @api.response(200,"Working hours successfully set")
    @api.response(400,"Working hours already existing")
    def post(self,restaurant_id):
        day = request.form.get('day')
        start = request.form.get('start')
        end = request.form.get('end')
        try :
            start = datetime.strptime(start, "%H:%M").time()
            end = datetime.strptime(end, "%H:%M").time()
        except Exception as e :
            return {"message": str(e)}, 500
        
        try:
            if 'x-amzn-oidc-accesstoken' in request.headers:
                access_token = request.headers.get('x-amzn-oidc-accesstoken')
            elif "access_token" in request.cookies:
                access_token=request.cookies.get("access_token")
            else:
                return "You are not logged in", 403
            
            user=get_user(access_token)
            if user is None:
                return "You are not logged in", 403
            restaurants = get_restaurant_by_owner(user.get('id'))
            if restaurants is None or int(restaurant_id) not in [restaurant.get('id') for restaurant in restaurants]:
                return "You are not the owner of this restaurant", 403
            
            #Modify the DB with the new description
            if get_working_hours(restaurant_id, day) is not None :
                returned = modify_working_hours(restaurant_id, day, start, end)
                if returned == None:
                    return {"message": "Not working"}, 500
                else :
                    print(get_working_hours(restaurant_id, day).opening_time)
                    return {"message": "Working hours successfully set", "restaurant_id": restaurant_id}, 200
            else :
                returned = add_working_hours(restaurant_id, day, start, end)
                return {"message": "Working hours successfully set", "restaurant_id": restaurant_id}, 200
        except Exception as e:
            return {"message": str(e)}, 500
        
api.route('/delete_picture/<int:restaurant_id>')
class DeleteImage(Resource):
    @api.doc("upload a picture")
    @api.expect({
        "picture_id":fields.Integer(required=True)
    })
    @api.response(200,"Picture deleted")
    @api.response(403,"You are not logged in")
    @api.response(403,"You are not the owner of this restaurant")
    @api.response(500,"Picture not deleted")
    def delete(self, restaurant_id):
        try:
            if 'x-amzn-oidc-accesstoken' in request.headers:
                access_token = request.headers.get('x-amzn-oidc-accesstoken')
            elif "access_token" in request.cookies:
                access_token=request.cookies.get("access_token")
            else:
                return "You are not logged in", 403
            
            user=get_user(access_token)
            if user is None:
                return "You are not logged in", 403
            restaurants = get_restaurant_by_owner(user.get('id'))
            if restaurants is None or int(restaurant_id) not in [restaurant.get('id') for restaurant in restaurants]:
                return "You are not the owner of this restaurant", 403
            

            data = request.json
            picture_id = data['picture_id']
            result = delete_picture(picture_id, restaurant_id)
            if result == True :
                return {"message": "Picture deleted", "restaurant_id": restaurant_id}, 200
            else : 
                return {"message": "Picture not deleted", "restaurant_id": restaurant_id}, 500
        except Exception as e :
            return 'Error', 500