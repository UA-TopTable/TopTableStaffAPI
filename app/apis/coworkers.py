from flask import request
from flask_restx import Namespace,Resource,fields
from sqlalchemy.exc import IntegrityError
from services.db_service import get_restaurant_by_owner, add_coworker_to_restaurant


api=Namespace("coworkers",path="/api/v1/coworkers",description="Operations for managing the restaurant coworkers")

add_coworker_model = api.model('AddCoworker', {
    'email': fields.String(required=True, description='Email of the coworker'),
    'restaurant_id': fields.Integer(required=True, description='ID of the restaurant')
})

@api.route("/<int:owner_id>")
class OwnerRestaurants(Resource):
    @api.doc("get owner's restaurants") 
    @api.response(200,description="owner's restaurants")
    def get(self,owner_id):
        restaurants = get_restaurant_by_owner(owner_id)

        return restaurants,200
    
@api.route("/add_coworker")
class AddCoworker(Resource):
    @api.doc("add coworker")
    @api.expect(add_coworker_model)
    @api.response(200,description="success")
    @api.response(400,"Wrong body")
    @api.response(404,"restaurant does not exist")
    def post(self):
        try:
            data=request.json
            email=data["email"]
            restaurant_id=data["restaurant_id"]

            response_code=add_coworker_to_restaurant(restaurant_id, email)
            return response_code

        except KeyError:
            return "Wrong body",400
        except IntegrityError:
            return "restaurant does not exist",404