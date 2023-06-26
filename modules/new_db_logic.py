from modules.connect_db import User, Uploaded_file, Directory
import secrets
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import copy


def add_user(engine, session, nickname:str, email:str, password:str, token=secrets.token_hex(16)):
    with session(autoflush=False, bind=engine) as db:
        new_user = User(email=email, nickname=nickname,
                        password=password, token=token)
        db.add(new_user)
        db.commit()
        new_user_id = new_user.id
    return new_user_id


def add_directory(engine, session, user_id:int, name_directory:str):
    with session(autoflush=False, bind=engine) as db:
        new_directory = Directory(user_id = user_id, name_directory = name_directory)
        db.add(new_directory)
        db.commit()        
        new_directory_id = new_directory.id
    return new_directory_id


def add_file(engine, session, user_id:int, directory_id:int, file:str, range_start:datetime, range_end:datetime, date=datetime.now()):
    with session(autoflush=False, bind=engine) as db:
        new_file = Uploaded_file(user_id = user_id, date=date,
                        directory_id = directory_id, file = file,
                        range_start = range_start, range_end = range_end)
        db.add(new_file)
        db.commit()     
        new_file_id = new_file.id
    return new_file_id


def check_user(engine, session, nickname:str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.nickname == nickname).first()
    return bool(user)


def authorization(engine, session, email:str, password:str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.email==email).filter(User.password==password).first()
    return bool(user)


def search_email_by_token(engine, session, token: str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.token == token).first()
    return user.email


def search_name_by_token(engine, session, token: str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.token == token).first()
    return user.nickname


def search_token_by_email(engine, session, email:str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.email == email).first()
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


def get_directories(engine, session, user_id: int):
    with session(autoflush=False, bind=engine) as db:
        directories = db.query(Directory).filter(Directory.user_id == user_id).all()
    return directories


def get_directory_id_by_name(engine, session, user_id: int, name_directory: str):
    with session(autoflush=False, bind=engine) as db:
        directory = db.query(Directory).filter(Directory.user_id==user_id, Directory.name_directory==name_directory).first()
    return directory.id


def get_directory_by_id(engine, session, directory_id:int): #get directory
    with session(autoflush=False, bind=engine) as db:
        directory = db.query(Directory).filter(Directory.id==directory_id).first()
    return directory


def get_dates(engine, session, user_id:int, first_date, second_date, limit=10):
    with session(autoflush=False, bind=engine) as db:
        files = db.query(Uploaded_file).filter(Uploaded_file.range_start>=first_date, Uploaded_file.range_end<=second_date).all()
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


def del_directory(engine, session, directory_id: int):
    with session(autoflush=False, bind=engine) as db:
        directory = db.query(Directory).filter(Directory.id == directory_id).first()
        db.delete(directory)
        db.commit()


def update_file(engine, session, file_id: int, new_name: str, date=datetime.now()):
    with session(autoflush=False, bind=engine) as db:
        file = db.query(Uploaded_file).filter(Uploaded_file.id == file_id).first()
        file.file = new_name
        file.date = date
        db.commit()


def update_name_directory(engine, session, directory_id: int, new_name: str):
    with session(autoflush=False, bind=engine) as db:
        directory = db.query(Directory).filter(Directory.id == directory_id).first()
        directory.name_directory = new_name
        db.commit()
