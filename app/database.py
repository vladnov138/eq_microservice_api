from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base


def create_bd(engine):
    Base.metadata.create_all(bind=engine)


def connect(name_db='main.db'):
    sqlite_database = f"sqlite:///database/{name_db}"
    engine = create_engine(sqlite_database)
    session = sessionmaker(autoflush=False, bind=engine)
    return engine, session


def clean_db(engine):
    Base.metadata.drop_all(engine)
