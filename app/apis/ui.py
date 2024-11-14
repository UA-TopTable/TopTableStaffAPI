import sys
import boto3
from urllib.parse import urlparse
from flask import make_response, render_template
from flask_restx import Namespace,Resource
from services.db_service import get_reservations, get_restaurant, get_all_tables, get_table_by_id, get_user_by_id, get_pictures, get_working_hours

api=Namespace("ui",description="UI-related endpoints")

@api.route("/restaurant/<int:id>")
class RestaurantPage(Resource):
    def get(self, id):
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


        print(restaurant,file=sys.stderr)
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