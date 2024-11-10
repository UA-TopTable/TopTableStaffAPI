from flask import json, jsonify, request
from flask_restx import Namespace,Resource,fields
from sqlalchemy.exc import IntegrityError
from services.db_service import add_table,get_all_tables,get_all_restaurants, get_reservations, update_reservation


api=Namespace("restaurant",path="/api/v1/restaurant",description="Operations for managing the restaurant information (including layout)")

dining_table_model=api.model("dining_table",{
    "id":fields.Integer,
    "description":fields.String(required=False),
    "table_number":fields.String,
    "number_of_seats":fields.Integer,
    "table_type":fields.String
})

reservation_model=api.model("reservation",{
    "id":fields.Integer,
    "user_id":fields.Integer,
    "restaurant_id":fields.Integer,
    "dining_table_id":fields.Integer,
    "number_of_people":fields.Integer,
    "reservation_start_time":fields.DateTime,
    "reservation_end_time":fields.DateTime,
    "status":fields.String,
    "special_requests":fields.String,
    "reservation_code":fields.String,
    "created_date":fields.DateTime,
    "updated_date":fields.DateTime
})

#add a table to a restaurant
@api.route("/<int:id>/tables",doc={"params":{"id":"restaurant_id"}})
class Tables(Resource):
    @api.doc("add table")
    @api.expect({
        "description":fields.String(required=False),
        "table_number":fields.String(required=True),
        "number_of_seats":fields.Integer(required=True),
        "table_type":fields.String(required=True)
    })
    @api.response(200,description="success",model=dining_table_model)
    @api.response(400,"Wrong body")
    @api.response(400,"table_type must be either 'indoors' or 'outdoors'")
    @api.response(400,"table_number must not have more than 3 digits")
    @api.response(404,"restaurant does not exist")
    def post(self,id):
        try:
            #do the data extraction
            data=request.json
            table_number=data["table_number"]
            number_of_seats=data["number_of_seats"]
            table_type=data["table_type"]

            #and let the service handle the rest
            table,response_code=add_table(table_number,number_of_seats,table_type,id,data["description"] if "description" in data else None)
            return table,response_code

        except KeyError:
            return "Wrong body",400
        except IntegrityError:
            return "restaurant does not exist",404

    @api.doc("get all tables") 
    @api.response(200,description="restaurant's tables",model=fields.List(fields.Nested(dining_table_model)))
    def get(self,id):
        tables=get_all_tables(id)

        return tables if tables else [],200
    
@api.route("/")
class Restaurants(Resource):
    @api.doc("get all restaurants") 
    @api.response(200,description="restaurants")
    def get(self):
        tables=get_all_restaurants()

        return tables,200
    
@api.route("/<int:id>/reservations",doc={"params":{"id":"restaurant_id"}})
class Reservations(Resource):
    @api.doc("show present reservations")
    @api.response(200,description="present reservations",model=fields.List(fields.Nested(reservation_model)))
    def get(self,id):
        reservations=get_reservations(id)

        return [reservation.as_dict() for reservation in reservations],200
    
    @api.doc("change reservation status")
    @api.expect({
        "status":fields.String(required=True,choices=["pending","confirmed","cancelled"]),
        "reservation_id":fields.Integer(required=True)
    })
    @api.response(200,description="success")
    @api.response(400,"Wrong body")
    @api.response(404,"reservation does not exist")
    def post(self,id):
        data=request.json
        
        if "status" not in data or data["status"] not in ["pending","confirmed","cancelled"] or "reservation_id" not in data:
            return "Wrong body",400

        status=data["status"]
        reservation_id=data["reservation_id"]

        result=update_reservation(id,reservation_id,status)

        if result is None:
            return "reservation does not exist",404
        else:
            return "success",200