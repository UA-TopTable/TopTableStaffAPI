from flask import request
from flask_restx import Namespace,Resource,fields
from sqlalchemy.exc import IntegrityError
from services.db_service import get_restaurant_by_owner, add_coworker_to_restaurant, remove_coworker
from services.auth_service import get_user


api=Namespace("coworkers",path="/api/v1/coworkers",description="Operations for managing the restaurant coworkers")

add_coworker_model = api.model('AddCoworker', {
    'email': fields.String(required=True, description='Email of the coworker'),
    'restaurant_id': fields.Integer(required=True, description='ID of the restaurant')
})

remove_coworker_model = api.model('RemoveCoworker', {
    'restaurant_id': fields.Integer(required=True, description='ID of the restaurant'),
    'user_id': fields.Integer(required=True, description='ID of the coworker')
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
    @api.response(403,"You are not the owner of this restaurant")
    def post(self):
        try:
            data=request.json
            email=data["email"]
            restaurant_id=data["restaurant_id"]

            access_token=request.cookies.get("access_token")
            user=get_user(access_token)
            restaurants = get_restaurant_by_owner(user.get('id'))
            if restaurants is None or int(restaurant_id) not in [restaurant.get('id') for restaurant in restaurants]:
                return "You are not the owner of this restaurant", 403

            try:
                response_code=add_coworker_to_restaurant(restaurant_id, email)
            except:
                return "coworker does not exist",404
            return response_code

        except KeyError:
            return "Wrong body",400
        except IntegrityError:
            return "restaurant does not exist",404
        

@api.route("/remove_coworker")
class RemoveCoworker(Resource):
    @api.doc("remove coworker")
    @api.expect(remove_coworker_model)
    @api.response(200,description="success")
    @api.response(404,"coworker does not exist")
    def delete(self):
        try:
            data=request.json
            restaurant_id=data["restaurant_id"]
            user_id=data["user_id"]

            access_token=request.cookies.get("access_token")
            user=get_user(access_token)
            restaurants = get_restaurant_by_owner(user.get('id'))
            if restaurants is None or int(restaurant_id) not in [restaurant.get('id') for restaurant in restaurants]:
                return "You are not the owner of this restaurant", 403

            response_code=remove_coworker(restaurant_id, user_id)
            return response_code

        except KeyError:
            return "Wrong body",400
        except IntegrityError:
            return "coworker does not exist",404