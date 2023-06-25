from modules.connect_db import User, Uploaded_file, Directory
import secrets
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import copy


def add_user(engine, session, email:str, nickname:str, password:str, token=secrets.token_hex(16)):
    with session(autoflush=False, bind=engine) as db:
        new_user = User(email=email, nickname=nickname,
                        password=password, token=token)
        db.add(new_user)
        db.commit()
        new_user_id = new_user.id
    
    engine.dispose()
    return copy.copy(new_user)


def add_directory(engine, session, user_id:int, name_directory:str):
    with session(autoflush=False, bind=engine) as db:
        new_directory = Directory(user_id = user_id, name_directory = name_directory)
        db.add(new_directory)
        db.commit()
    engine.dispose()
    return copy.copy(new_directory)


def add_file(engine, session, user_id:int, directory_id:int, file:str, range_start:datetime, range_end:datetime, date=datetime.now()):
    with session(autoflush=False, bind=engine) as db:
        new_file = Uploaded_file(user_id = user_id, date=date,
                        directory_id = directory_id, file = file,
                        range_start = range_start, range_end = range_end)
        db.add(new_file)
        db.commit()
        new_file_id = new_file.id
    engine.dispose()
    return copy.copy(new_file)


def check_user(engine, session, nickname:str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.nickname==nickname).first()
    return bool(user)


def authorization(engine, session, email:str, password:str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.email==email).filter(User.password==password).first()
    return bool(user)


def search_by_token(engine, session, token:str): #get email
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.token==token).first()
    return user.email


def search_by_email(engine, session, email:str): # get token
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.email==email).first()
    return user.token


def get_user_id(engine, session, nickname:str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.nickname==nickname).first()
    return user.id


def get_files(engine, session, user_id:int, sort_max=0, limit=10):
    if sort_max:
        with session(autoflush=False, bind=engine) as db:
            files = db.query(Uploaded_file).filter(Uploaded_file.user_id==user_id).order_by(Uploaded_file.date.asc()).limit(limit).all()
    
    else:
        with session(autoflush=False, bind=engine) as db:
            files = db.query(Uploaded_file).filter(Uploaded_file.user_id==user_id).order_by(Uploaded_file.date.desc()).limit(limit).all()
    return files


def get_dates(engine, session, user_id:int, first_date, second_date):
    with session(autoflush=False, bind=engine) as db:
        files = db.query(Uploaded_file).filter(Uploaded_file.date>=first_date, Uploaded_file.date<=second_date).all()
    return files


def del_user(engine, session, nickname:str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.nickname==nickname).first()
        db.delete(user)
        db.commit()


def del_file(engine, session, file_id:int):
    with session(autoflush=False, bind=engine) as db:
        file = db.query(Uploaded_file).filter(Uploaded_file.id==file_id).first()
        db.delete(file)
        db.commit()


def update_file(engine, session, file_id:int, new_file:str, date=datetime.now()):
    with session(autoflush=False, bind=engine) as db:
        file = db.query(Uploaded_file).filter(Uploaded_file.id==file_id).first()
        file.file = new_file
        file.date = date

        db.commit()





    







