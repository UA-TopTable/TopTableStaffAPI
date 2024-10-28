from flask import json, jsonify, request
from flask_restx import Namespace,Resource,fields
from services.db_service import add_table,get_all_tables


api=Namespace("Restaurant management",description="Operations for managing the restaurant information (including layout)")

dining_table_model=api.model("dining_table",{
    "id":fields.Integer,
    "description":fields.String,
    "table_number":fields.String,
    "number_of_seats":fields.Integer,
    "table_type":fields.String
})

#add a table to a restaurant
@api.route("/restaurant/<id>/tables",doc={"params":{"id":"restaurant_id"}})
class Tables(Resource):
    @api.doc("add table")
    @api.expect({
        "description":fields.String(required=False),
        "table_number":fields.String(required=True),
        "number_of_seats":fields.Integer(required=True),
        "table_type":fields.String(required=True)
    })
    @api.response(200,dining_table_model)
    @api.response(400,"Wrong body")
    @api.response(400,"table_type must be either 'indoors' or 'outdoors'")
    @api.response(400,"table_number must not have more than 3 digits")
    def post(self,id):
        try:
            #do the data extraction
            data=request.json
            table_number=data["table_number"]
            number_of_seats=data["number_of_seats"]
            table_type=data["table_type"]

            #and let the service handle the rest
            table,response_code=add_table(table_number,number_of_seats,table_type,id,data["description"] if "description" in data else None)
            return json.dumps(table),response_code

        except KeyError:
            return "Wrong body",400

    @api.doc("get all tables") 
    @api.response(200,"returns all tables from restaurant (empty list if the restaurant doesn't exist or doesn't have tables")
    def get(self,id):
        tables,response_code=get_all_tables(id)

        return tables,response_code