from modules.connect_db import User, Uploaded_file, Directory, sqlite_database, engine, session
import datetime
import secrets
from sqlalchemy import create_engine


def add_user(email:str, nickname:str, password:str, token=secrets.token_hex(16)):
    with session(autoflush=False, bind=engine) as db:
        new_user = User(email=email, nickname=nickname,
                        password=password, token=token)
        db.add(new_user)
        db.commit()


def add_file(user_id, directory_id, file, range_start, range_end, date=str(datetime.now())):
    with session(autoflush=False, bind=engine) as db:
        new_file = User(user_id = user_id, date=date,
                        directory_id = directory_id, file = file,
                        range_start = range_start, range_end = range_end)
        db.add(new_user)
        db.commit()
