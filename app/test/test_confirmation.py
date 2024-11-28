from random import choice
from string import ascii_letters
import boto3
from moto import mock_aws
import pytest
import socketio


from app import app
from services.queue_service import delete_reservation_confirmation, get_reservation_confirmation
from data.models.Reservation import Reservation
from data.models.DiningTable import DiningTable
from data.models.Restaurant import Restaurant
from data.db_engine import engine,Base
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta

example_tables=[]
example_restaurants=[]
wrong_tables=[]
example_reservations=[]
restaurant_id=0

def generate_unique_string(size=10):
    my_list = [choice(ascii_letters) for _ in range(size)] 
    my_str = ''.join(my_list) 
    return my_str 

def generate_unique_string(size=10):
    my_list = [choice(ascii_letters) for _ in range(size)] 
    my_str = ''.join(my_list) 
    return my_str 

#Note: in a "real situation" these (and most other tests), would not use the same services(db,user pool,...) and would use copies made specifically for testing. So, we can make some assumptions in our tests
@pytest.fixture(scope="session",autouse=True)
def setup():
    global example_tables,example_restaurants,wrong_tables,restaurant_id,example_reservations

    example_tables=[DiningTable(description="test table 1",table_number="1a",number_of_seats=2,table_type="indoor",restaurant_id=0),DiningTable(description="test table 2",table_number="2a",number_of_seats=2,table_type="indoor",restaurant_id=0)]
    example_restaurants=[Restaurant(name="test restaurant 1",location_latitude=1.2,location_longitude=4.5)]
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


@pytest.mark.timeout(10) #fails if it takes more than 10s
@mock_aws
def test_get_and_delete_from_queue():
    sqs = boto3.client('sqs', region_name='us-east-1')
    queue=sqs.create_queue(QueueName='test_queue')
    queue_url=queue['QueueUrl']

    sqs.send_message(QueueUrl=queue_url,MessageBody=str({"reservation":example_reservations[0].as_dict()}))

    message=get_reservation_confirmation([restaurant_id],sqs=sqs,queue_url=queue_url)

    assert message["Body"] == str({"reservation":example_reservations[0].as_dict()})

    delete_reservation_confirmation(message["ReceiptHandle"],sqs=sqs,queue_url=queue_url)

    response_after = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['ApproximateNumberOfMessages'])
    num_messages_after = int(response_after['Attributes']['ApproximateNumberOfMessages'])

    assert num_messages_after == 0

    sqs.delete_queue(QueueUrl=queue_url)
    