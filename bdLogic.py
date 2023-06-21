
import sqlite3
import secrets #needed to generate a token
from datetime import datetime

def create_db():    
    db = sqlite3.connect('main.db')
    cursor = db.cursor()

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
    db.close()


def add_user(email, nickname, password, token = secrets.token_hex(16)):    
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO users(email, nickname, password, token) VALUES('"+email+"', '"+nickname+"', '"+password+"', '"+token+"')")
    db.commit()
    db.close()


def add_file(user_id, file, date=str(datetime.now())):    
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO uploaded_files(user_id, date, file) VALUES('"+str(user_id)+"', '"+date+"', '"+file+"')")
    db.commit()
    db.close()

def select_all():    
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users'")
    answer = cursor.fetchall()
    db.close()
    return answer

def check_user(nickname):    
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE nickname=='"+nickname+"'")
    answer = len(cursor.fetchall())
    db.close()
    return answer

def authorization(email, password):    
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email=='"+email+"' AND password=='"+password+"'")
    answer = len(cursor.fetchall())
    db.close()
    return answer
    
def search_by_token(token):    
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE token=='"+token+"'")
    answer = cursor.fetchall()[0][2]
    db.close()
    return answer


def del_user(nickname):    
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE nickname=='"+nickname+"'")
    db.commit()
    db.close()


def del_file(file_id):    
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM uploaded_files WHERE id=='"+file_id+"'")
    db.commit()
    db.close()

del_file('3')
