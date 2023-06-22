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
        print('gg', new_user.id)

add_user('gg_boy@mail.ru', 'gg_boy', '1234')
