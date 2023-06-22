from sqlalchemy import create_engine
from sqlalchemy import  Column, Integer, String, DateTime, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

name_db = 'newbd.db'

sqlite_database = f"sqlite:///../database/{name_db}"

engine = create_engine(sqlite_database)

session = sessionmaker(autoflush=False, bind=engine)

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String)
    nickname = Column(String)
    password = Column(String)
    token = Column(String)

class Uploaded_file(Base):
    __tablename__ = "uploaded_files"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    date = Column(DateTime)
    file = Column(Text)
    range_start = Column(DateTime)
    range_end = Column(DateTime)

class Directory(Base):
    __tablename__ = "directories"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    name_directory = Column(Text)

def create_bd():
    Base.metadata.create_all(bind=engine)

create_bd()
