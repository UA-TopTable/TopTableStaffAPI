import sys
import boto3
from urllib.parse import urlparse
from flask import make_response, render_template
from flask_restx import Namespace,Resource
from services.db_service import get_reservations, get_restaurant, get_all_tables, get_table_by_id, get_user_by_id, get_pictures, get_working_hours, get_restaurant_by_owner

api=Namespace("ui",description="UI-related endpoints")

@api.route("/restaurant/<int:id>")
class RestaurantPage(Resource):
    def get(self, id):
        #TODO: get connected user
        restaurants = get_restaurant_by_owner(1)
        print(restaurants)
        print(id)
        if id not in [restaurant.get('id') for restaurant in restaurants]:
            return make_response("You are not the owner of this restaurant", 403)


        tables = get_all_tables(id)
        restaurant = get_restaurant(id)[0]
        pictures = get_pictures(id)
        working_hours = get_working_hours(id, None)
        if not (pictures == [] or pictures is None):
            for picture in pictures : 
                parsed_url = urlparse(picture['link'])
                
                bucket_name = parsed_url.netloc.split('.')[0]
                object_key = parsed_url.path.lstrip('/')
                s3_client = boto3.client('s3')
                signed_url = s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': bucket_name, 'Key': object_key},
                        ExpiresIn=3600 
                )
                print(signed_url)
                picture['link'] = signed_url

        if restaurant is None:
            return make_response("No restaurant found", 404)
        if tables is None:
            return make_response("No tables for this restaurant", 404)
        else:
            return make_response(
                render_template("manage_restaurant.html", restaurant=restaurant, tables=tables, pictures = pictures, working_hours = working_hours),
                200,
                {'Content-Type': 'text/html'}
            )

@api.route("/restaurant/<int:id>/reservations")
class ReservationsPage(Resource):
    def get(self, id):
        reservations_raw=get_reservations(id)
        print(reservations_raw,file=sys.stderr)

        reservations=[]
        #get table number and customer name to make it more human-readable
        for reservation in reservations_raw:
            reservation=reservation.as_dict()

            table=get_table_by_id(reservation['dining_table_id'])
            reservation['table_number']=table.table_number if table is not None else ""

            user=get_user_by_id(reservation['user_id'])
            reservation['customer_name']=user.full_name if user is not None else ""

            reservations.append(reservation)

        return make_response(
            render_template("reservations.html", reservations=reservations,restaurant_id=id),
            200,
            {'Content-Type': 'text/html'}
        )


@api.route("/home")
class HomePage(Resource):
    def get(self):
        #TODO: get connected user
        restaurants = get_restaurant_by_owner(1)

        return make_response(
            render_template("index.html", restaurants=restaurants),
            200,
            {'Content-Type': 'text/html'}
        )


import json
from datetime import datetime
from services.db_service import add_restaurant, add_table, add_working_hours, add_reservation, save_user_account
@api.route("/mock_data")
class MockDataPage(Resource):
    def get(self):
        print("mock")

        user_data = {
        "full_name": "Test User Restaurant Owner",
        "email": "testuser@example.com",
        "phone": "1234567890",
        "profile_image_url": "http://example.com/image.jpg",
        "user_type": "admin",
        "password_hash": "passwordhsh"
        }
        user = save_user_account(user_data)
        user_id = user.get('id')
        restaurant_data = {
            "name": "Restaurant Test",
            "description": "Restaurant Test",
            "location_address": "Address 1",
            "location_latitude": "1",
            "location_longitude": "1",
            "restaurant_image": "image1",
            "time_zone": "UTC",
            "owner_user_id": user_id
        }
        restaurant =  add_restaurant(restaurant_data)
        restr_id = restaurant.get('id')
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days_of_week:
            add_working_hours(restaurant_id=restr_id, day_of_week=day, opening_time="09:00", closing_time="21:00")
        table1 = add_table(table_number="1",restaurant_id=restr_id,number_of_seats=4, table_type="indoor", description="Table 1")
        table2 = add_table(table_number="2",restaurant_id=restr_id,number_of_seats=4, table_type="indoor", description="Table 2")
        table_id = json.loads(table1[0]).get('id')
        reservation_start_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        reservation_end_time = reservation_start_time.replace(hour=10, minute=30)
        reservation_code = str(int(datetime.timestamp(datetime.now())))[-10:]
        add_reservation(user_id=user_id, restaurant_id=restr_id, dining_table_id=table_id, number_of_people=4, reservation_code=reservation_code,
                        reservation_start_time=reservation_start_time, reservation_end_time=reservation_end_time)


        return make_response("Successfully mocked data", 200)