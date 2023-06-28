from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


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
    directory_id = Column(Integer)
    file = Column(Text)
    range_start = Column(DateTime)
    range_end = Column(DateTime)


class Directory(Base):
    __tablename__ = "directories"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    name_directory = Column(Text)
