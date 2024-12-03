import pytest
import requests
from data.models.Restaurant import Restaurant
from data.models.UserAccount import UserAccount
from data.models.RestaurantOwners import RestaurantOwners
from data.models.DiningTable import DiningTable
from data.db_engine import engine,Base
from sqlalchemy.orm import Session
from services.db_service import add_coworker_to_restaurant, get_restaurant_by_owner, remove_coworker
from services.auth_service import get_user

ACCESS_TOKEN = 'eyJraWQiOiIxQmJZNmxxTEhzdzQzalZGdEtaaWZUZ0twSnppQStHMmVyVVdhS255SExFPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzNGY4NTRlOC05MDYxLTcwYjAtY2I5OC1kOTc1YzA1OTZkNDIiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9KbEM1VkZoNlUiLCJ2ZXJzaW9uIjoyLCJjbGllbnRfaWQiOiI0dGVoNWJqdnQxazg0ZmhhYzE0aGtra2QydiIsIm9yaWdpbl9qdGkiOiJhYzlhNWMzNS0zMTg4LTRlZjYtOTY5YS1jMmFiMDAwN2JjZjkiLCJldmVudF9pZCI6IjZhZTAwMmU0LTM3MjAtNDkyYy05NWRhLWU1ZTc3MmMyMTBjOSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoicGhvbmUgb3BlbmlkIHByb2ZpbGUgZW1haWwiLCJhdXRoX3RpbWUiOjE3MzMyMzU4MTcsImV4cCI6MTczMzIzOTQxNywiaWF0IjoxNzMzMjM1ODE3LCJqdGkiOiIwN2FkZDg2My03NDQwLTRhNzItYjQ4OC1hMjdmNDQ1YmRhNDYiLCJ1c2VybmFtZSI6InRlc3QxIn0.HNsknqUlRBQnxpaYNz9BzRwWgmKj7fmXINDi_XSOdWEXdvt7Jk_CBSsakqUj2RgJLdoJ0r_yJ5T3USGGeWhx6C45vEpqIg2VASQkpsyy--jE5ydm6dxOp8is7xU-AX_w4Y-Ikua0AiC2MFz1v8gjqwJ--7ezWB0ahITQ8jUY_nHs09xFdo5XPp6jnZOSxe2a5PhRk9VkdpyRb9JoxMa1sreC-glr3y348q3vteH5C0mu_ebuI0ixlF1MBuXrfWRwwRxqzkc0sY3Iv1JwV1gw4o5cgKy2ABw3prLHIKiJ_HGoRkD6ezn9a_-g-ZUeiQvasahtJeQQjySzQH3pqoiSgA'

@pytest.fixture(scope="function",autouse=True)
def setup():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


    with Session(engine,expire_on_commit=False) as session:

        session.add(UserAccount(id=1, full_name="User1",email="user1@example.com",phone="1234567890",user_type="admin",password_hash="password"))
        session.add(UserAccount(id=2, full_name="User2",email="user2@example.com",phone="1234567890",user_type="admin",password_hash="password"))

        session.commit()

        session.add(Restaurant(id=1, name="Restaurant 1",location_latitude=1,location_longitude=1))
        session.add(Restaurant(id=2, name="Restaurant 2",location_latitude=1,location_longitude=1))

        session.commit()

        session.add(DiningTable(description="test table 1",table_number="1a",number_of_seats=2,table_type="indoor",restaurant_id=1))
        session.add(DiningTable(description="test table 2",table_number="2a",number_of_seats=2,table_type="indoor",restaurant_id=2))

        session.commit()
    yield


def test_add_coworker():
    add_coworker_to_restaurant(restaurant_id=1,user_email="user1@example.com")
    assert len(get_restaurant_by_owner(owner_id=1))==1

def test_remove_coworker():
    add_coworker_to_restaurant(restaurant_id=1,user_email="user1@example.com")
    assert len(get_restaurant_by_owner(owner_id=1))==1
    remove_coworker(restaurant_id=1,user_id=1)
    assert get_restaurant_by_owner(owner_id=1) is None

def test_manage_restaurant(client):
    access_token = ACCESS_TOKEN
    user = get_user(access_token)
    add_coworker_to_restaurant(restaurant_id=1,user_email=user.get('email'))
    client.set_cookie("access_token",access_token)
    response = client.get("/staff/ui/restaurant/1")
    assert response.status_code==200

def test_manage_restaurant_fail(client):
    access_token = ACCESS_TOKEN
    user = get_user(access_token)
    add_coworker_to_restaurant(restaurant_id=1,user_email=user.get('email'))
    client.set_cookie("access_token",access_token)
    response = client.get("/staff/ui/restaurant/2")
    assert response.status_code==403

def test_manage_restaurant_fail_coworker_removed(client):
    access_token = ACCESS_TOKEN
    user = get_user(access_token)
    add_coworker_to_restaurant(restaurant_id=1,user_email=user.get('email'))
    client.set_cookie("access_token",access_token)
    response = client.get("/staff/ui/restaurant/1")
    assert response.status_code==200
    remove_coworker(restaurant_id=1,user_id=user.get('id'))
    response = client.get("/staff/ui/restaurant/1")
    assert response.status_code==403