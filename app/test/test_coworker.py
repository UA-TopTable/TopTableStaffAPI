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
    access_token = "eyJraWQiOiIxQmJZNmxxTEhzdzQzalZGdEtaaWZUZ0twSnppQStHMmVyVVdhS255SExFPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzNGY4NTRlOC05MDYxLTcwYjAtY2I5OC1kOTc1YzA1OTZkNDIiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9KbEM1VkZoNlUiLCJ2ZXJzaW9uIjoyLCJjbGllbnRfaWQiOiI3dGExb25wM2E2YnUzZTluNWt2aWdudWV0ZCIsIm9yaWdpbl9qdGkiOiJhN2VlMGZlZS1lNGRmLTRhZjAtYWMwMC0zNzgyNjY2NDIxMjQiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiYXV0aF90aW1lIjoxNzMyNDQ4MjU5LCJleHAiOjE3MzI0NTE4NTksImlhdCI6MTczMjQ0ODI1OSwianRpIjoiMTA4YzAzNDUtZmZiOC00Zjg4LTg0MGYtMjkyNGJmMWE0ZDMyIiwidXNlcm5hbWUiOiJ0ZXN0MSJ9.CCfM4RP_O7Ppve9V2vQf_44qZn75t_L-ESIew7YZuN62euUUWPot5KJk9N74Tt0rig1BTRi6Z7xZ17luOqDoMGZD5excevTD9NGhtaJnjtbTjQTQ3aT5LiJ6cfeodvl7bU5I3mO7-GM-VEcqo7noLHl0GAJt0So_bjs7ncU6IjvhGNJzO7YazAG0oxCPJI9UVcCN4jP7Ie5HezQjT20rj_fON_vSlQEU5PvrL4mk42nRBTPo9ke17pkTEillEifdl3sXmCvxA2GsoFM9TW2SpM8ti5PPrzLkCHDJaU8bTYzOU4QW5672E0GiXsVq8n0zj9o19CRqNT_0UWdwv-Sw3A"
    user = get_user(access_token)[0]
    add_coworker_to_restaurant(restaurant_id=1,user_email=user.get('email'))
    client.set_cookie("access_token",access_token)
    response = client.get("/staff/ui/restaurant/1")
    assert response.status_code==200

def test_manage_restaurant_fail(client):
    access_token = "eyJraWQiOiIxQmJZNmxxTEhzdzQzalZGdEtaaWZUZ0twSnppQStHMmVyVVdhS255SExFPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzNGY4NTRlOC05MDYxLTcwYjAtY2I5OC1kOTc1YzA1OTZkNDIiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9KbEM1VkZoNlUiLCJ2ZXJzaW9uIjoyLCJjbGllbnRfaWQiOiI3dGExb25wM2E2YnUzZTluNWt2aWdudWV0ZCIsIm9yaWdpbl9qdGkiOiJhN2VlMGZlZS1lNGRmLTRhZjAtYWMwMC0zNzgyNjY2NDIxMjQiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiYXV0aF90aW1lIjoxNzMyNDQ4MjU5LCJleHAiOjE3MzI0NTE4NTksImlhdCI6MTczMjQ0ODI1OSwianRpIjoiMTA4YzAzNDUtZmZiOC00Zjg4LTg0MGYtMjkyNGJmMWE0ZDMyIiwidXNlcm5hbWUiOiJ0ZXN0MSJ9.CCfM4RP_O7Ppve9V2vQf_44qZn75t_L-ESIew7YZuN62euUUWPot5KJk9N74Tt0rig1BTRi6Z7xZ17luOqDoMGZD5excevTD9NGhtaJnjtbTjQTQ3aT5LiJ6cfeodvl7bU5I3mO7-GM-VEcqo7noLHl0GAJt0So_bjs7ncU6IjvhGNJzO7YazAG0oxCPJI9UVcCN4jP7Ie5HezQjT20rj_fON_vSlQEU5PvrL4mk42nRBTPo9ke17pkTEillEifdl3sXmCvxA2GsoFM9TW2SpM8ti5PPrzLkCHDJaU8bTYzOU4QW5672E0GiXsVq8n0zj9o19CRqNT_0UWdwv-Sw3A"
    user = get_user(access_token)[0]
    add_coworker_to_restaurant(restaurant_id=1,user_email=user.get('email'))
    client.set_cookie("access_token",access_token)
    response = client.get("/staff/ui/restaurant/2")
    assert response.status_code==403

def test_manage_restaurant_fail_coworker_removed(client):
    access_token = "eyJraWQiOiIxQmJZNmxxTEhzdzQzalZGdEtaaWZUZ0twSnppQStHMmVyVVdhS255SExFPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzNGY4NTRlOC05MDYxLTcwYjAtY2I5OC1kOTc1YzA1OTZkNDIiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9KbEM1VkZoNlUiLCJ2ZXJzaW9uIjoyLCJjbGllbnRfaWQiOiI3dGExb25wM2E2YnUzZTluNWt2aWdudWV0ZCIsIm9yaWdpbl9qdGkiOiJhN2VlMGZlZS1lNGRmLTRhZjAtYWMwMC0zNzgyNjY2NDIxMjQiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiYXV0aF90aW1lIjoxNzMyNDQ4MjU5LCJleHAiOjE3MzI0NTE4NTksImlhdCI6MTczMjQ0ODI1OSwianRpIjoiMTA4YzAzNDUtZmZiOC00Zjg4LTg0MGYtMjkyNGJmMWE0ZDMyIiwidXNlcm5hbWUiOiJ0ZXN0MSJ9.CCfM4RP_O7Ppve9V2vQf_44qZn75t_L-ESIew7YZuN62euUUWPot5KJk9N74Tt0rig1BTRi6Z7xZ17luOqDoMGZD5excevTD9NGhtaJnjtbTjQTQ3aT5LiJ6cfeodvl7bU5I3mO7-GM-VEcqo7noLHl0GAJt0So_bjs7ncU6IjvhGNJzO7YazAG0oxCPJI9UVcCN4jP7Ie5HezQjT20rj_fON_vSlQEU5PvrL4mk42nRBTPo9ke17pkTEillEifdl3sXmCvxA2GsoFM9TW2SpM8ti5PPrzLkCHDJaU8bTYzOU4QW5672E0GiXsVq8n0zj9o19CRqNT_0UWdwv-Sw3A"
    user = get_user(access_token)[0]
    add_coworker_to_restaurant(restaurant_id=1,user_email=user.get('email'))
    client.set_cookie("access_token",access_token)
    response = client.get("/staff/ui/restaurant/1")
    assert response.status_code==200
    remove_coworker(restaurant_id=1,user_id=user.get('id'))
    response = client.get("/staff/ui/restaurant/1")
    assert response.status_code==403