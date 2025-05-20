from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "postgresql+psycopg2://myuser:mysecretpassword@localhost:5461/datakvalitet"
engine = create_engine(DATABASE_URL)
session = sessionmaker(bind=engine)
session = session()


def init_db():
    Base.metadata.create_all(bind=engine)