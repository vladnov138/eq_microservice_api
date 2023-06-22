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


def search_by_token(token:str): #get email
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.token==token).first()
    return user.email


def search_by_email(email): # get token
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.email==email).first()
    return user.token


def get_user_id(nickname):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.nickname==nickname).first()
    return user.id


def get_files(user_id, sort_max=0, limit=10):
    if sort_max:
        with session(autoflush=False, bind=engine) as db:
            files = db.query(Uploaded_file).filter(Uploaded_file.user_id==user_id).order_by(Uploaded_file.date.asc()).limit(limit).all()
    
    else:
        with session(autoflush=False, bind=engine) as db:
            files = db.query(Uploaded_file).filter(Uploaded_file.user_id==user_id).order_by(Uploaded_file.date.desc()).limit(limit).all()
    return files


def get_dates(user_id, first_date, second_date):
    with session(autoflush=False, bind=engine) as db:
        files = db.query(Uploaded_file).filter(Uploaded_file.date>=first_date, Uploaded_file.date<=second_date).all()
    return files








