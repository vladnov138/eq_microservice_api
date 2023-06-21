
import sqlite3
import secrets #needed to generate a token


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





db.close()
