
import sqlite3
import secrets #needed to generate a token
from datetime import datetime


db = sqlite3.connect('main.db')

cursor = db.cursor()

def create_db():
    cursor.execute("""
        CREATE TABLE users (
                id integer PRIMARY KEY AUTOINCREMENT,
                email text,
                nickname text,
                password text,
                token text
        )
    """)
    db.commit()

    cursor.execute("""
        CREATE TABLE uploaded_files (
                id integer PRIMARY KEY AUTOINCREMENT,
                user_id integer,
                date datetime,
                file integer
        )
    """)
    
    db.commit()


def add_user(email, nickname, password, token = secrets.token_hex(16)):
    cursor.execute(f"INSERT INTO users(email, nickname, password, token) VALUES('"+email+"', '"+nickname+"', '"+password+"', '"+token+"')")
    db.commit()



def add_file(user_id, file, date=str(datetime.now())):
    cursor.execute(f"INSERT INTO uploaded_files(user_id, date, file) VALUES('"+str(user_id)+"', '"+date+"', '"+file+"')")
    db.commit()

def select_all():
    cursor.execute("SELECT * FROM users'")
    print(cursor.fetchall(), len(cursor.fetchall()))


def check_user(nickname):
    cursor.execute("SELECT * FROM users WHERE nickname=='"+nickname+"'")
    return len(cursor.fetchall())

def authorization(email, password):
    cursor.execute("SELECT * FROM users WHERE email=='"+email+"' AND password=='"+password+"'")
    return len(cursor.fetchall())
    
def search_by_token(token):
    cursor.execute("SELECT * FROM users WHERE token=='"+token+"'")
    return cursor.fetchall()[0][2]

db.close()
