import boto3
from flask_restx import Namespace, Resource, fields
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from flask import request
from werkzeug.utils import secure_filename
from services.db_service import add_picture, delete_working_hours, get_reservations, remove_coworker, delete_reservation, get_coworkers_by_restaurant_id, get_all_tables, delete_table, delete_restaurant, get_pictures, get_restaurant, edit_restaurant_main_picture, edit_food_category, get_picture_by_id, add_restaurant, modify_description, add_working_hours, get_working_hours, modify_working_hours, delete_picture, get_restaurant_by_owner
from services.auth_service import get_user
from datetime import datetime
from string import ascii_letters, digits
from random import choice
from os.path import splitext
from secret import S3_BUCKET


AWS_REGION="us-east-1"

api=Namespace("upload", path="/api/v1/upload", description="Operations to upload pictures and description of the restaurant")

s3_client = boto3.client('s3', region_name=AWS_REGION)
s3_delete = boto3.resource('s3', region_name=AWS_REGION)

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
        i=0
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
                if i == 0 and get_restaurant(restaurant_id)[0]['restaurant_image'] == '' :
                    edit_restaurant_main_picture(restaurant_id, file_url)
                i+=1

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
        
@api.route('/delete_picture/<int:restaurant_id>')
class DeletePicture(Resource):
    @api.doc("Delete a picture")
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
            picture = get_picture_by_id(picture_id)
            restaurant = get_restaurant(restaurant_id)[0]

            if picture is None :
                return {"message": "Picture not found", "restaurant_id": restaurant_id}, 500
            if restaurant is None :
                return {"message": "Restaurant not found", "restaurant_id": restaurant_id}, 500
            
            result = delete_picture(picture_id, restaurant_id)
            
            if result == True :
                if picture['link'] == restaurant['restaurant_image'] :
                    restaurant_pictures = get_pictures(restaurant_id)
                    edit_main_picture = None
                    if restaurant_pictures is not None and len(restaurant_pictures) > 0 :
                        edit_main_picture = edit_restaurant_main_picture(restaurant_id, restaurant_pictures[0]['link'])
                    else :
                        edit_main_picture = edit_restaurant_main_picture(restaurant_id, '')
                        return {"message": "Picture deleted, no other pictures available to be main picture", "restaurant_id": restaurant_id}, 200
                    if edit_main_picture == False :
                        edit_main_picture = edit_restaurant_main_picture(restaurant_id, '')
                        return {"message": "Picture deleted, not possible to change the main picture", "restaurant_id": restaurant_id}, 200
                try :
                    s3_delete.Object(bucket_name = S3_BUCKET, key = picture['link'])
                except Exception as e :
                    return {"message": 'Error : ' + str(e)}, 500
                return {"message": "Picture deleted", "restaurant_id": restaurant_id}, 200
            else : 
                return {"message": "Picture not deleted", "restaurant_id": restaurant_id}, 500
        except Exception as e :
            return {"message": 'Error : ' + str(e)}, 500
        

@api.route('/create_restaurant/')
class CreateRestaurant(Resource):
    @api.doc("Create a restaurant")
    @api.response(200,"Restaurant created")
    @api.response(403,"You are not logged in")
    @api.response(500,"Restaurant not created")
    def post(self):
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

            data = {}
            data['name']=request.form['name']
            data['description']=request.form['description']
            data['location_address']=request.form['location_address']
            data['owner_user_id']=request.form['owner_user_id']
            data['food_category'] = request.form['food_category'].upper()
            restaurant_image = request.files.get('restaurant_image')
            uploaded_url = []

            if restaurant_image.filename == '':
                return {"message": "Invalid file name"}, 400
            
            filename = secure_filename(restaurant_image.filename)

            _, extension = splitext(filename)
            filename = generate_random_string(32) + extension

            if filename == '':
                return {"message": "Invalid file name"}, 400
            
            filename = secure_filename(filename)

            try:
                # Upload de l'image à S3
                s3_client.upload_fileobj(
                    restaurant_image,
                    S3_BUCKET,
                    filename
                )

                file_url = f"https://{S3_BUCKET}.s3.{S3_BUCKET}.amazonaws.com/{filename}"
                uploaded_url.append(file_url)

            except (NoCredentialsError, PartialCredentialsError):
                return {"message": "Missing credentials"}, 500
            except Exception as e:
                return {"message": str(e)}, 500

            data['restaurant_image']=uploaded_url[0]
            result = add_restaurant(data)

            if isinstance(result, dict) :
                restaurant_id = result['id']
                #Fill in the DB with the new image
                add_picture(file_url, restaurant_id)
                return {"message": "Restaurant created", "restaurant_id": result['id']}, 200
            else : 
                return {"message": "Restaurant not created"}, 500
        except Exception as e :
            return f'Error : {e}', 500
        

@api.route('/edit_food_category/<int:restaurant_id>')
class EditFoodCategory(Resource):
    @api.doc("Edit the food category")
    @api.expect({
        "food_category":fields.String(required=True)
    })
    @api.response(200,"Food category edited")
    @api.response(403,"You are not logged in")
    @api.response(403,"You are not the owner of this restaurant")
    @api.response(500,"Food category not edited")
    def post(self, restaurant_id):
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
            food_category = data['food_category']
            result = edit_food_category(food_category, restaurant_id)
            if result:
                return {"message": "Food category edited", "restaurant_id": restaurant_id}, 200
            else: 
                return {"message": "Food category not edited", "restaurant_id": restaurant_id}, 500
        except Exception as e :
            return {"message": 'Error : ' + str(e)}, 500
        
@api.route('/edit_main_picture/<int:restaurant_id>')
class EditRestaurantMainPicture(Resource):
    @api.doc("Edit the picture showed in the home page")
    @api.expect({
        "picture_id":fields.String(required=True)
    })
    @api.response(200,"Main picture edited")
    @api.response(403,"You are not logged in")
    @api.response(403,"You are not the owner of this restaurant")
    @api.response(500,"Main picture not edited")
    def post(self, restaurant_id):
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
            picture = get_picture_by_id(picture_id)
            result = edit_restaurant_main_picture(restaurant_id, picture['link'])
            if result:
                return {"message": "Main picture edited", "restaurant_id": restaurant_id}, 200
            else: 
                return {"message": "Main picture not edited", "restaurant_id": restaurant_id}, 500
        except Exception as e :
            return {"message": 'Error : ' + str(e)}, 500
        
@api.route('/delete_restaurant/<int:restaurant_id>')
class DeleteRestaurant(Resource):
    @api.doc("Delete a restaurant")
    @api.response(302,"Restaurant deleted")
    @api.response(403,"You are not logged in")
    @api.response(500,"Restaurant not deleted")
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
            

            pictures = get_pictures(restaurant_id)
            dining_tables = get_all_tables(restaurant_id)
            coworkers = get_coworkers_by_restaurant_id(restaurant_id)
            reservs = get_reservations(restaurant_id)
            reservations = [reservation.as_dict() for reservation in reservs]
            working_hours = get_working_hours(restaurant_id, None)
            

            if pictures is not None :
                for picture in pictures :
                    try :
                        s3_delete.Object(bucket_name = S3_BUCKET, key = picture['link'])
                        delete_picture(picture['id'], restaurant_id)
                    except Exception as e :
                        return {"message": 'Error with pictures : ' + str(e)}, 500

            if dining_tables is not None :
                for table in dining_tables :
                    try :
                        delete_table(table['id'])
                    except Exception as e :
                        return {"message": 'Error with tables : ' + str(e)}, 500
           
            if reservations is not None :    
                for reservation in reservations :
                    try :
                        delete_reservation(reservation['id'])
                    except Exception as e :
                        return {"message": 'Error with reservations : ' + str(e)}, 500
              
            if coworkers is not None :
                for coworker in coworkers :
                    try :
                        remove_coworker(restaurant_id, coworker['id'])
                    except Exception as e :
                        return {"message": 'Error with coworkers : ' + str(e)}, 500
          
            if working_hours is not None :
                for working_hour in working_hours :
                    try :
                        delete_working_hours(restaurant_id, working_hour['day_of_week'])
                    except Exception as e :
                        return {"message": 'Error with working hours: ' + str(e)}, 500
          
            try :
                result = delete_restaurant(restaurant_id)
            except Exception as e :
                return {"message": 'Error with restaurant : ' + str(e)}, 500
            if result:
                return {"message": "Restaurant deleted", "restaurant_id": restaurant_id}, 302
            else: 
                return {"message": f"Restaurant not deleted : {result}", "restaurant_id": restaurant_id}, 500

        except Exception as e :
            return {"message": 'General Error : ' + str(e)}, 500
