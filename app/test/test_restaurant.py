from datetime import datetime, timedelta
from random import choice
from string import ascii_letters
import pytest
from data.models.Reservation import Reservation
from data.models.DiningTable import DiningTable
from data.models.Restaurant import Restaurant
from data.db_engine import engine,Base
from sqlalchemy.orm import Session
from sqlalchemy import func, text

example_tables=[]
example_restaurants=[]
wrong_tables=[]
example_reservations=[]
restaurant_id=0

def generate_unique_string(size=10):
    my_list = [choice(ascii_letters) for _ in range(size)] 
    my_str = ''.join(my_list) 
    return my_str 

#Note: in a "real situation" these (and most other tests), would not use the same services(db,user pool,...) and would use copies made specifically for testing. So, we can make some assumptions in our tests
@pytest.fixture(scope="session",autouse=True)
def setup():
    global example_tables,example_restaurants,wrong_tables,restaurant_id,example_reservations

    example_tables=[DiningTable(description="test table 1",table_number="1a",number_of_seats=2,table_type="indoor",restaurant_id=0),DiningTable(description="test table 2",table_number="2a",number_of_seats=2,table_type="indoor",restaurant_id=0)]
    example_restaurants=[Restaurant(name="test restaurant 1",location_latitude=123,location_longitude=456)]
    wrong_tables=[DiningTable(description="wrong table 1",table_number="1a",number_of_seats=2,table_type="wooden",restaurant_id=0),DiningTable(description="wrong table 2",table_number="1aaaaaaaaaaaaaaa",number_of_seats=2,table_type="indoor",restaurant_id=0)]
    
    restaurant_id=0

    Base.metadata.create_all(engine)
    with Session(engine,expire_on_commit=False) as session:
        session.add(example_restaurants[0])
        session.commit()
        session.refresh(example_restaurants[0])

        restaurant_id=example_restaurants[0].id
        for table in example_tables+wrong_tables:
            table.restaurant_id=restaurant_id
    
        
        
        session.add(example_tables[0])
        session.commit()
        session.refresh(example_tables[0])

        example_reservations=[
            Reservation(user_id=1,restaurant_id=restaurant_id,dining_table_id=example_tables[0].id,reservation_start_time=datetime.now()-timedelta(minutes=30),reservation_end_time=datetime.now()+timedelta(minutes=30),number_of_people=2,status="pending",special_requests="none",reservation_code=generate_unique_string(size=10),created_date=datetime.now(),updated_date=datetime.now()),
            Reservation(user_id=1,restaurant_id=restaurant_id,dining_table_id=example_tables[0].id,reservation_start_time=datetime.now()-timedelta(minutes=30),reservation_end_time=datetime.now()+timedelta(minutes=30),number_of_people=2,status="pending",special_requests="none",reservation_code=generate_unique_string(size=10),created_date=datetime.now(),updated_date=datetime.now()),
            Reservation(user_id=1,restaurant_id=restaurant_id,dining_table_id=example_tables[0].id,reservation_start_time=datetime.now()-timedelta(minutes=30),reservation_end_time=datetime.now()+timedelta(minutes=30),number_of_people=2,status="pending",special_requests="none",reservation_code=generate_unique_string(size=10),created_date=datetime.now(),updated_date=datetime.now()),
        ]



        session.add(example_reservations[0])
        session.add(example_reservations[1])
        session.add(example_reservations[2])
        session.commit()

    yield

    with Session(engine) as session:
        session.execute(text("DELETE FROM WorkingHours;"))
        session.execute(text("DELETE FROM Reservation;"))
        session.execute(text("DELETE FROM DiningTable;"))
        session.execute(text("DELETE FROM Restaurant;"))
        session.commit()

def test_fetch_tables_correct_restaurant_id(client):
    global restaurant_id
    response=client.get(f"/api/v1/restaurant/{restaurant_id}/tables")

    assert response.status_code==200
    assert isinstance(response.json,list)
    assert len(response.json)!=0
        
def test_fetch_tables_incorrect_restaurant_id(client):
    response=client.get(f"/api/v1/restaurant/{restaurant_id+1000}/tables")

    assert response.status_code==200
    assert isinstance(response.json,list)
    assert len(response.json)==0

def test_add_table_correct_restaurant_id(client):
    global restaurant_id,example_tables
    table=example_tables[1]
    response=client.post(f"/api/v1/restaurant/{restaurant_id}/tables",json={"description":table.description,"table_number":table.table_number,"table_type":table.table_type,"number_of_seats":table.number_of_seats})
    assert response.status_code==200


def test_add_table_incorrect_restaurant_id(client):
    global example_tables,restaurant_id
    table=example_tables[1]
    response=client.post(f"/api/v1/restaurant/{restaurant_id+1000}/tables",json={"description":table.description,"table_number":table.table_number,"table_type":table.table_type,"number_of_seats":table.number_of_seats})
    assert response.status_code==404

def test_add_table_wrong_type(client):
    global restaurant_id,wrong_tables
    table=wrong_tables[0]
    response=client.post(f"/api/v1/restaurant/{restaurant_id}/tables",json={"description":table.description,"table_number":table.table_number,"table_type":table.table_type,"number_of_seats":table.number_of_seats})
    assert response.status_code==400

def test_add_table_wrong_number(client):
    global restaurant_id,wrong_tables
    table=wrong_tables[1]
    response=client.post(f"/api/v1/restaurant/{restaurant_id}/tables",json={"description":table.description,"table_number":table.table_number,"table_type":table.table_type,"number_of_seats":table.number_of_seats})
    assert response.status_code==400

def test_get_reservations(client):
    global example_reservations
    response=client.get(f"/api/v1/restaurant/{restaurant_id}/reservations")
    assert response.status_code==200
    assert isinstance(response.json,list)
    assert len(response.json)==len(example_reservations)
    
def test_get_reservations_wrong_restaurant(client):
    global example_reservations
    response=client.get(f"/api/v1/restaurant/{restaurant_id+1000}/reservations")
    assert response.status_code==200
    assert isinstance(response.json,list)
    assert len(response.json)==0

def test_cancel_reservation(client):
    global example_reservations
    response=client.post(f"/api/v1/restaurant/{restaurant_id}/reservations",json={"status":"cancelled","reservation_id":example_reservations[0].id})
    assert response.status_code==200

    with Session(engine) as session:
        reservation=session.get(Reservation,example_reservations[0].id)
        assert reservation.status=="cancelled"