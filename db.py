from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "postgresql+psycopg2://postgres:password1234@localhost:5432/datakvalitet"
engine = create_engine(DATABASE_URL)
session = sessionmaker(bind=engine)
session = session()


def init_db():
    Base.metadata.create_all(bind=engine)