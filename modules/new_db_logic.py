from modules.connect_db import User, Uploaded_file, Directory, sqlite_database, engine, session
import secrets
from sqlalchemy import create_engine
from datetime import datetime


def add_user(email:str, nickname:str, password:str, token=secrets.token_hex(16)):
    with session(autoflush=False, bind=engine) as db:
        new_user = User(email=email, nickname=nickname,
                        password=password, token=token)
        db.add(new_user)
        db.commit()


def add_directory(user_id:int, name_directory:str):
    with session(autoflush=False, bind=engine) as db:
        new_directory = Directory(user_id = user_id, name_directory = name_directory)
        db.add(new_directory)
        db.commit()


def add_file(user_id:int, directory_id:int, file:str, range_start:datetime, range_end:datetime, date=datetime.now()):
    with session(autoflush=False, bind=engine) as db:
        new_file = Uploaded_file(user_id = user_id, date=date,
                        directory_id = directory_id, file = file,
                        range_start = range_start, range_end = range_end)
        db.add(new_file)
        db.commit()


def check_user(nickname:str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.nickname==nickname).first()
    return bool(user)


def authorization(email:str, password:str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.email==email).filter(User.password==password).first()
    return bool(user)



