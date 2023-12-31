from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base


def create_bd(engine):
    Base.metadata.create_all(bind=engine)


def connect(name_db='newbd.db'):
    sqlite_database = f"sqlite:///../database/{name_db}"
    engine = create_engine(sqlite_database)
    session = sessionmaker(autoflush=False, bind=engine)
    return engine, session