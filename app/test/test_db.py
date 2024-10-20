from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from data.models.UserAccount import UserAccount
host = 'localhost'
port = 3306
user = 'root'
password = 'admin123'
database = 'toptable'
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

def test_simple_query():
    engine = create_engine(DATABASE_URL)

    userAccount = UserAccount(full_name="Ilker Atik", email="ilkeratik35@gmail.com",
                               user_type="admin", phone= '938100200', 
                               profile_image_url='https://avatars.githubusercontent.com/u/44725644?v=4',
                               password_hash="$2y$10$KVAh7/V0WbsxVbKF9FG06.PZOO8RLcAyPT.pb5Z4ZeFa.xv0N.xJq")

    with engine.connect() as connection:
        Session = sessionmaker(bind=engine)
        session = Session()
        user = session.query(UserAccount).filter_by(email=userAccount.email).first()
        if user:
            session.delete(user)
            session.commit()
        session.add(userAccount)
        session.commit()
        result = session.query(UserAccount).filter_by(email=userAccount.email).first()
        print(f"UserAccount(full_name='{result.full_name}', email='{result.email}', user_type='{result.user_type}',
               phone='{result.phone}', profile_image_url='{result.profile_image_url}', password_hash='{result.password_hash}')")


