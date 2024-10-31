import pytest
from data.models.DiningTable import DiningTable
from data.models.Restaurant import Restaurant
from data.db_engine import engine
from sqlalchemy.orm import Session
from sqlalchemy import func, text

example_tables=[DiningTable(description="test table 1",table_number="1a",number_of_seats=2,table_type="indoors",restaurant_id=0),DiningTable(description="test table 2",table_number="2a",number_of_seats=2,table_type="indoors",restaurant_id=0)]
example_restaurants=[Restaurant(name="test restaurant 1",location_latitude=123,location_longitude=456)]
wrong_tables=[DiningTable(description="wrong table 1",table_number="1a",number_of_seats=2,table_type="wooden",restaurant_id=0),DiningTable(description="wrong table 2",table_number="1aaaaaaaaaaaaaaa",number_of_seats=2,table_type="indoors",restaurant_id=0)]
restaurant_id=0

#Note: in a "real situation" these (and most other tests), would not use the same services(db,user pool,...) and would use copies made specifically for testing. So, we can make some assumptions in our tests
@pytest.fixture(autouse=True)
def setup():
    global example_tables,example_restaurants,restaurant_id

    with Session(engine) as session:
        session.add(example_restaurants[0])
        session.commit()

        restaurant_id=session.query(Restaurant).all()[0].id
        for table in example_tables+wrong_tables:
            table.restaurant_id=restaurant_id
    
        
        session.add(example_tables[0])
        session.commit()

    yield

def test_fetch_tables_correct_restaurant_id(client):
    global restaurant_id
    response=client.get(f"/api/v1/restaurant/{restaurant_id}/tables")

    assert response.status_code==200
    assert isinstance(response.json,list)
    assert len(response.json)==1
        
def test_fetch_tables_incorrect_restaurant_id(client):
    response=client.get("/api/v1/restaurant/1/tables")

    assert response.status_code==200
    assert isinstance(response.json,list)
    assert len(response.json)==0

def test_add_table_correct_restaurant_id(client):
    global restaurant_id
    table=example_tables[1]
    response=client.post(f"/api/v1/restaurant/{restaurant_id}/tables",json={"description":table.description,"table_number":table.table_number,"table_type":table.table_type,"number_of_seats":table.number_of_seats})
    assert response.status_code==200


def test_add_table_incorrect_restaurant_id(client):
    table=example_tables[1]
    response=client.post("/api/v1/restaurant/1/tables",json={"description":table.description,"table_number":table.table_number,"table_type":table.table_type,"number_of_seats":table.number_of_seats})
    assert response.status_code==404

def test_add_table_wrong_type(client):
    global restaurant_id
    table=wrong_tables[0]
    response=client.post(f"/api/v1/restaurant/{restaurant_id}/tables",json={"description":table.description,"table_number":table.table_number,"table_type":table.table_type,"number_of_seats":table.number_of_seats})
    assert response.status_code==400

def test_add_table_wrong_number(client):
    global restaurant_id
    table=wrong_tables[1]
    response=client.post(f"/api/v1/restaurant/{restaurant_id}/tables",json={"description":table.description,"table_number":table.table_number,"table_type":table.table_type,"number_of_seats":table.number_of_seats})
    assert response.status_code==400