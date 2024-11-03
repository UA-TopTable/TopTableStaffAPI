from flask import json
from data.models.Restaurant import Restaurant
from data.models.DiningTable import DiningTable
from data.models.UserAccount import UserAccount
from sqlalchemy.orm import Session
from data.db_engine import engine
from sqlalchemy.orm.exc import NoResultFound



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
        return json.dumps(table.to_dict()) if as_json else table,200

def get_all_tables(restaurant_id,as_json=True):
    with Session(engine) as session:
        tables=session.query(DiningTable).filter(DiningTable.restaurant_id==restaurant_id).order_by(DiningTable.table_number).all()
        return [table.to_dict() for table in tables] if as_json else tables,200
    
def get_restaurant(restaurant_id,as_json=True):
    with Session(engine) as session:
        restaurant=session.get(Restaurant,restaurant_id)
        if restaurant is not None and as_json:
            return restaurant.to_dict(),200
        else:
            return restaurant,200
    
def get_all_restaurants(as_json=True):
    with Session(engine) as session:
        restaurants=session.query(Restaurant).order_by(Restaurant.id).all()
        return [r.to_dict() for r in restaurants] if as_json else restaurants,200
    
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
    