from data.models import Restaurant
from data.models.DiningTable import DiningTable
from sqlalchemy.orm import Session
from data.db_engine import engine



def add_table(table_number,number_of_seats,table_type,restaurant_id,description=None):
    if get_restaurant(restaurant_id) is None:
        return "restaurant does not exist",404

    if table_type not in ["indoors","outdoors"]:
        return "table_type must be either 'indoors' or 'outdoors'",400
    if len(table_number)>3:
        return "table_number must not have more than 3 digits",400
    if description is not None:
        table=DiningTable(description=description,table_number=table_number,number_of_seats=number_of_seats,table_type=table_type,restaurant_id=restaurant_id)
    else:
        table=DiningTable(table_number=table_number,number_of_seats=number_of_seats,table_type=table_type,restaurant_id=restaurant_id)
    
    with Session(engine) as session:
        session.add(table)
        session.commit()
        return table,200

def get_all_tables(restaurant_id):
    with Session(engine) as session:
        tables=session.query(DiningTable).filter(DiningTable.restaurant_id==restaurant_id).order_by(DiningTable.table_number).all()
        return tables,200
    
def get_restaurant(restaurant_id):
    with Session(engine) as session:
        return session.query(Restaurant).get(restaurant_id)