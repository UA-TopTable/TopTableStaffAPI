from flask import render_template
from flask_restx import Namespace,Resource
from services.db_service import get_restaurant,get_all_tables

api=Namespace("ui",description="UI-related endpoints")

@api.route("/restaurant/<int:id>")
class RestaurantPage(Resource):
    def get(self,id):
        restaurant=get_restaurant(id)
        if restaurant is None:
            return "Restaurant not found",404
        else:
            tables=get_all_tables
            return render_template("restaurant.html",restaurant=restaurant,tables=tables)