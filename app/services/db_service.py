from decimal import Decimal
from flask import json
from data.models.RestaurantOwners import RestaurantOwners
from data.models.Reservation import Reservation
from data.models.Restaurant import Restaurant
from data.models.DiningTable import DiningTable
from data.models.UserAccount import UserAccount
from data.models.RestaurantPictures import RestaurantPictures
from data.models.WorkingHours import WorkingHours
from sqlalchemy.orm import Session,make_transient
from data.db_engine import engine
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound 
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
    
def save_user_account(user_data: dict):
    if user_data.get('phone') is None:
        user_data['phone'] = ''
    if user_data.get('profile_image_url') is None:
        user_data['profile_image_url'] = ''
    if user_data.get('user_type') is None:
        user_data['user_type'] = 'customer'
    with Session(engine) as session:
        existing_user = session.query(UserAccount).filter(UserAccount.email == user_data.get('email')).first()
        if existing_user:
            existing_user.full_name = user_data.get('full_name')
            existing_user.phone = user_data.get('phone')
            existing_user.profile_image_url = user_data.get('profile_image_url')
            existing_user.user_type = user_data.get('user_type')
            existing_user.password_hash = user_data.get('password_hash')
            user = existing_user
        else:
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

def get_user_account(user_id):
    with Session(engine) as session:
        user = session.get(UserAccount, user_id)
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
        if day_of_week is not None : 
            with Session(engine) as session:
                return session.query(WorkingHours).filter(WorkingHours.restaurant_id==restaurant_id, WorkingHours.day_of_week == day_of_week).one()
        else : 
            with Session(engine) as session:
                working_hours = session.query(WorkingHours).filter(WorkingHours.restaurant_id==restaurant_id).all()  
            return [w.as_dict() for w in working_hours] if working_hours else None
    except NoResultFound:
        return None
    except MultipleResultsFound :
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
        working_hours = session.merge(working_hours)
        working_hours.opening_time = opening_time
        working_hours.closing_time = closing_time
        session.commit()
        return working_hours.as_dict() if working_hours else None

def delete_working_hours(restaurant_id, day_of_week):
    try :
        working_hours = get_working_hours(restaurant_id, day_of_week)
        if working_hours is None :
            return None
        with Session(engine) as session:
            session.delete(working_hours)
            session.commit()
            return True
    except :
        return None

def get_reservations(restaurant_id):
    with Session(engine) as session:
        return session.query(Reservation).filter(
            Reservation.restaurant_id == restaurant_id).all()

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
    
def add_picture(picture_link, restaurant_id):
    with Session(engine) as session :
        picture = RestaurantPictures(
            link = picture_link,
            restaurant_id = restaurant_id
        )
        session.add(picture)
        session.commit()
        return picture.as_dict() if picture else None
    
def get_pictures(restaurant_id):
    with Session(engine) as session :
        pictures = session.query(RestaurantPictures).filter(RestaurantPictures.restaurant_id == restaurant_id).all()
        return [picture.as_dict() for picture in pictures] if pictures else None

def get_picture_by_id(picture_id):
    try :
        with Session(engine) as session :
            picture = session.query(RestaurantPictures).filter(RestaurantPictures.id == picture_id).one()
            return picture.as_dict() if picture else None
    except :
        return None

def delete_picture(picture_id, restaurant_id):
    with Session(engine) as session :
        try :
            picture = session.query(RestaurantPictures).filter(RestaurantPictures.restaurant_id == restaurant_id, RestaurantPictures.id == picture_id).one()
        except :
            return False
        session.delete(picture)
        session.commit()
        return True

def add_restaurant(restaurant_data: dict):
    with Session(engine) as session:
        restaurant = Restaurant(
            name=restaurant_data['name'],
            description=restaurant_data.get('description'),
            location_address=restaurant_data.get('location_address'),
            location_latitude=1,
            location_longitude=1,
            restaurant_image=restaurant_data.get('restaurant_image'),
            time_zone='UTC',
            owner_user_id=restaurant_data.get('owner_user_id'),
            food_category=restaurant_data.get('food_category')
        )
        session.add(restaurant)
        session.commit()

        restaurantOwner = RestaurantOwners(user_id = restaurant_data.get('owner_user_id'), restaurant_id = restaurant.id)
        session.add(restaurantOwner)
        session.commit()
        return restaurant.as_dict() if restaurant else None
    
def add_reservation(user_id,restaurant_id,dining_table_id,number_of_people,reservation_start_time
                    ,reservation_end_time,reservation_code,special_requests=''):
    with Session(engine) as session:
        table = session.get(DiningTable, dining_table_id)
        if table is None:
            return None
        
        reservation = Reservation(
            user_id=user_id,
            restaurant_id=restaurant_id,
            dining_table_id=dining_table_id,
            number_of_people=number_of_people,
            reservation_start_time=reservation_start_time,
            reservation_end_time=reservation_end_time,
            status='pending',
            special_requests=special_requests,
            reservation_code=reservation_code)
        session.add(reservation)
        session.commit()
        return reservation.as_dict() if reservation else None
    

def get_restaurant_by_owner(owner_id):
    with Session(engine) as session:
        restaurant_ids = session.query(RestaurantOwners.restaurant_id).filter(RestaurantOwners.user_id == owner_id).all()
        restaurant_ids = [r[0] for r in restaurant_ids]
        restaurants = session.query(Restaurant).filter(Restaurant.id.in_(restaurant_ids)).all()
        return [r.as_dict() for r in restaurants] if restaurants else None

def get_coworkers_by_restaurant_id(restaurant_id):
    with Session(engine) as session:
        user_ids = session.query(RestaurantOwners).filter(RestaurantOwners.restaurant_id == restaurant_id).all()
        user_ids = [r.user_id for r in user_ids]
        users = session.query(UserAccount).filter(UserAccount.id.in_(user_ids)).all()
        return [r.as_dict() for r in users] if users else None

def add_coworker_to_restaurant(restaurant_id, user_email):
    with Session(engine) as session:
        user = session.query(UserAccount).filter(UserAccount.email == user_email).first()
        restaurant_owner = RestaurantOwners(user_id=user.id, restaurant_id=restaurant_id)
        session.add(restaurant_owner)
        session.commit()
        return restaurant_owner.as_dict() if restaurant_owner else None
    
def remove_coworker(restaurant_id, user_id):
    with Session(engine) as session:
        restaurant_owner = session.query(RestaurantOwners).filter(RestaurantOwners.restaurant_id == restaurant_id, RestaurantOwners.user_id == user_id).first()
        session.delete(restaurant_owner)
        session.commit()
        return restaurant_owner.as_dict() if restaurant_owner else None
    

def get_all_restaurants_by_owner_email(email):
    with Session(engine) as session:
        user_account=session.query(UserAccount).filter(UserAccount.email == email).first()

        if user_account is None:
            return None
        return get_restaurant_by_owner(user_account.id)
    
def get_reservation_by_id(reservation_id):
    with Session(engine) as session:
        reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
        return reservation.as_dict() if reservation else None
    
def edit_food_category(food_category, restaurant_id):
    with Session(engine) as session:
        restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        restaurant.food_category = food_category
        session.commit()
        return restaurant.as_dict() if restaurant else None
    
def edit_restaurant_main_picture(restaurant_id, picture_link):
    try :
        with Session(engine) as session:
            restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
            restaurant.restaurant_image = picture_link
            session.commit()
            return restaurant.as_dict() if restaurant else None
    except :
        return None
    
def delete_restaurant(restaurant_id):
    try :
        with Session(engine) as session:
            restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
            if restaurant is None:
                return None
            session.delete(restaurant)
            session.commit()
            return True
    except :
        return None
    
def delete_table(table_id):
    try :
        with Session(engine) as session:
            table = session.query(DiningTable).filter(DiningTable.id == table_id).first()
            if table is None:
                return None
            session.delete(table)
            session.commit()
            return True
    except :
        return None

def delete_reservation(reservation_id):
    try :
        with Session(engine) as session:
            reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
            if reservation is None:
                return None
            session.delete(reservation)
            session.commit()
            return True
    except :
        return None