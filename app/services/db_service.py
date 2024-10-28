from app.data.models import DiningTable
from data.db_session import session


class DBService():
    def add_table(self,table_number,number_of_seats,table_type,restaurant_id,description=None):
        if table_type not in ["indoors","outdoors"]:
                return "table_type must be either 'indoors' or 'outdoors'",400
        if len(table_number)>3:
            return "table_number must not have more than 3 digits",400
        if description is not None:
            table=DiningTable(description=description,table_number=table_number,number_of_seats=number_of_seats,table_type=table_type,restaurant_id=restaurant_id)
        else:
            table=DiningTable(table_number=table_number,number_of_seats=number_of_seats,table_type=table_type,restaurant_id=restaurant_id)
        
        session.add(table)
        session.commit(table)
        return table,200
    
    def get_all_tables(self,restaurant_id):
        tables=session.query(DiningTable).filter(DiningTable.restaurant_id==restaurant_id).order_by(DiningTable.table_number).all()
        return tables,200