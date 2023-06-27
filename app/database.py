from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base


def create_bd(engine):  # create all tables
    Base.metadata.create_all(bind=engine)


def connect(name_db='main.db', way=''):
    sqlite_database = f"sqlite://{way}/database/{name_db}"
    engine = create_engine(sqlite_database)
    session = sessionmaker(autoflush=False, bind=engine)
    return engine, session


def clean_db(engine):  # delete all tables
    Base.metadata.drop_all(engine)
