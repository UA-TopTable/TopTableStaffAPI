import pytest
from data.db_engine import engine,Base
from services.db_service import add_restaurant, get_restaurant, edit_food_category

@pytest.fixture(scope="function",autouse=True)
def setup():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def test_add_food_category():
    restaurantData = {"id": 1, "name": "Restaurant 1", "location_latitude": 1, "location_longitude": 1, "food_category": "Italian"}
    add_restaurant(restaurant_data=restaurantData)
    restaurant = get_restaurant(restaurant_id=1)[0]
    assert restaurant.get('food_category').value == "Italian"

def test_edit_food_category():
    restaurantData = {"id": 1, "name": "Restaurant 1", "location_latitude": 1, "location_longitude": 1, "food_category": "Italian"}
    add_restaurant(restaurant_data=restaurantData)
    edit_food_category(restaurant_id=1,food_category="Japanese")
    restaurant = get_restaurant(restaurant_id=1)[0]
    assert restaurant.get('food_category').value == "Japanese"