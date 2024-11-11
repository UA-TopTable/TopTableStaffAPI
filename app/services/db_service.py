from flask import json
from data.models.Reservation import Reservation
from data.models.Restaurant import Restaurant
from data.models.DiningTable import DiningTable
from data.models.UserAccount import UserAccount
from data.models.RestaurantPictures import RestaurantPictures
from data.models.WorkingHours import WorkingHours
from sqlalchemy.orm import Session,make_transient
from data.db_engine import engine
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime



def add_table(table_number,number_of_seats,table_type,restaurant_id,description=None,as_json=True):
    if get_restaurant(restaurant_id,as_json=False) is None:
        return "restaurant does not exist",404

    if table_type not in ["indoor","outdoor"]:
        return "table_type must be either 'indoor' or 'outdoor'",400
    if len(table_number)>3:
        return "table_number must not have more than 3 digits",400
    if description is not None:
        table=DiningTable(description=description,table_number=table_number,number_of_seats=number_of_seats,table_type=table_type,restaurant_id=restaurant_id)
    else:
        table=DiningTable(table_number=table_number,number_of_seats=number_of_seats,table_type=table_type,restaurant_id=restaurant_id)
    
    with Session(engine) as session:
        session.add(table)
        session.commit()
        return json.dumps(table.as_dict()) if as_json else table,200

def get_all_tables(restaurant_id):
    with Session(engine) as session:
        tables=session.query(DiningTable).filter(DiningTable.restaurant_id==restaurant_id).all()
        return [table.as_dict() for table in tables] if tables else None
    
def get_restaurant(restaurant_id,as_json=True):
    with Session(engine) as session:
        restaurant=session.get(Restaurant,restaurant_id)
        if restaurant is not None and as_json:
            return restaurant.as_dict(),200
        else:
            return restaurant,200
    
def get_all_restaurants(as_json=True):
    with Session(engine) as session:
        restaurants=session.query(Restaurant).order_by(Restaurant.id).all()
        return [r.as_dict() for r in restaurants] if as_json else restaurants,200
    
def add_user_account(user_data: dict):
    if user_data.get('phone') is None:
        user_data['phone'] = ''
    if user_data.get('profile_image_url') is None:
        user_data['profile_image_url'] = ''
    if user_data.get('user_type') is None:
        user_data['user_type'] = 'regular'
    with Session(engine) as session:
        
        user = UserAccount(
            full_name=user_data.get('full_name'),
            email=user_data.get('email'),
            phone=user_data.get('phone'),
            profile_image_url=user_data.get('profile_image_url'),
            user_type=user_data.get('user_type'),
            password_hash=user_data.get('password_hash')
        )

        session.add(user)
        session.commit()
        
        return user.as_dict() if user else None

def get_user_by_email(email):
    try:
        with Session(engine) as session:
            return session.query(UserAccount).filter(UserAccount.email==email).one()
    except NoResultFound:
        return None
    
    
def add_picture(picture_link, restaurant_id):
    with Session(engine) as session :
        picture = RestaurantPictures(
            link = picture_link,
            restaurant_id = restaurant_id
        )
        session.add(picture)
        session.commit()
        return picture.as_dict() if picture else None

def modify_description(description, restaurant_id):
    if description == '' or description is None :
        description = ''
    with Session(engine) as session :
        restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not restaurant :
            return None
        restaurant.description = description
        session.commit()
        return restaurant.as_dict() if restaurant else None
    
def get_working_hours(restaurant_id, day_of_week):
    try:
        with Session(engine) as session:
            return session.query(WorkingHours).filter(WorkingHours.restaurant_id==restaurant_id, WorkingHours.day_of_week == day_of_week).one()
    except NoResultFound:
        return None

def add_working_hours(restaurant_id,day_of_week,opening_time,closing_time):
    if get_restaurant(restaurant_id) is None:
        return "restaurant does not exist",404
    if day_of_week.lower() not in ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']:
        return "day_of_week must be a valid day of the week",400
    if opening_time>=closing_time:
        return "closing_time must be after opening_time",400
    with Session(engine) as session:
        working_hours=WorkingHours(restaurant_id=restaurant_id,day_of_week=day_of_week,opening_time=opening_time,closing_time=closing_time)
        session.add(working_hours)
        session.commit()
        return working_hours.as_dict() if working_hours else None
    
def modify_working_hours(restaurant_id, day_of_week,opening_time,closing_time):
    working_hours = get_working_hours(restaurant_id, day_of_week)
    if working_hours is None :
        return "Not found in the DB", 500
    with Session(engine) as session:
        working_hours.opening_time = opening_time
        working_hours.closing_time = closing_time
        session.commit()
        return working_hours.as_dict() if working_hours else None

def get_reservations(restaurant_id):
    with Session(engine) as session:
        return session.query(Reservation).filter(
            Reservation.restaurant_id == restaurant_id,Reservation.status in ['pending','confirmed'],
            Reservation.reservation_start_time <= datetime.now(),
            Reservation.reservation_end_time >= datetime.now()).all()

def update_reservation(restaurant_id,reservation_id,status):
    with Session(engine, expire_on_commit=False) as session:
        reservation = session.query(Reservation).filter(Reservation.id == reservation_id,Reservation.restaurant_id==restaurant_id).first()
        if reservation is None:
            return None
        
        reservation.status = status
        session.commit()
        session.refresh(reservation)
        make_transient(reservation)
        return reservation
    
def get_table_by_id(table_id):
    try:
        with Session(engine) as session:
            return session.query(DiningTable).filter(DiningTable.id==table_id).one()
    except NoResultFound:
        return None
    
def get_user_by_id(user_id):
    try:
        with Session(engine) as session:
            return session.query(UserAccount).filter(UserAccount.id==user_id).one()
    except NoResultFound:
        return None
    