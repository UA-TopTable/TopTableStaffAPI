from flask import request
from flask_restx import Namespace,Resource,fields
from app.data.models import DiningTable
from data.db_session import session


api=Namespace("Restaurant management",description="Operations for managing the restaurant information (including layout)")

def add_table(table:DiningTable):
    session.add(table)
    session.commit()


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
    @api.response(200,"Success")
    @api.response(400,"Wrong body")
    @api.response(400,"table_type must be either 'indoors' or 'outdoors'")
    @api.response(400,"table_number must not have more than 3 digits")
    def post(self,id):
        try:
            data=request.json
            table_number=data["table_number"]
            number_of_seats=data["number_of_seats"]
            table_type=data["table_type"]

            if table_type not in ["indoors","outdoors"]:
                return "table_type must be either 'indoors' or 'outdoors'",400
            if len(table_number)>3:
                return "table_number must not have more than 3 digits",400
            
            if "description" in data:
                table=DiningTable(description=data["description"],table_number=table_number,number_of_seats=number_of_seats,table_type=table_type)
            else:
                table=DiningTable(table_number=table_number,number_of_seats=number_of_seats,table_type=table_type)

            add_table(table)
            return "Success",200

        except KeyError:
            return "Wrong body",400
        
    def get(self,id):
        pass