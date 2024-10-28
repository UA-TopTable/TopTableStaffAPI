from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from data.db_secrets import user,password,host,port,database

DATABASE_URL=f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)