import sqlite3
import secrets
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
                file text,
                range_start datetime,
                range_end datetime
        )
    """)

    db.commit()
    db.close()


def add_user(nickname, email, password, token=secrets.token_hex(16)):
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users(email, nickname, password, token) VALUES('" + email + "', '" + nickname + "', '" + password + "', '" + token + "')")
    db.commit()
    db.close()


def add_file(user_id, file, date=str(datetime.now())):
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("INSERT INTO uploaded_files(user_id, date, file) VALUES('" + str(
        user_id) + "', '" + date + "', '" + file + "')")
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
    cursor.execute("SELECT * FROM users WHERE nickname=='" + nickname + "'")
    answer = len(cursor.fetchall())
    db.close()
    return answer


def authorization(email, password):
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email=='" + email + "' AND password=='" + password + "'")
    answer = len(cursor.fetchall())
    db.close()
    return answer


def search_by_token(token):
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE token=='" + token + "'")
    answer = cursor.fetchall()[0][2]
    db.close()
    return answer


def search_by_email(email):  # get token
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email=='" + email + "'")
    answer = cursor.fetchall()[0][4]
    db.close()
    return answer


def get_user_id(nickname):
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE nickname=='" + nickname + "'")
    answer = cursor.fetchall()[0][0]
    db.close()
    return answer


def del_user(nickname):
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE nickname=='" + nickname + "'")
    db.commit()
    db.close()


def del_file(file_id):
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM uploaded_files WHERE id=='" + file_id + "'")
    db.commit()
    db.close()


def update_file(file_id, new_file, date=str(datetime.now())):
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("UPDATE uploaded_files SET file='" + new_file + "', date='" + date + "' WHERE id=='" + file_id + "'")
    db.commit()
    db.close()


def get_files(user_id, sorted_by='date', sort_max=0, limit=10):
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    _sorted = ['ASC', 'DESC']
    cursor.execute(
        "SELECT * FROM uploaded_files WHERE user_id=='" + str(user_id) + "' ORDER BY " + sorted_by + " " + _sorted[
            sort_max] + " LIMIT " + str(limit) + "")
    answer = cursor.fetchall()
    db.close()
    return answer


def get_dates(user_id, first_date, second_date):
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM uploaded_files WHERE user_id=='" + str(
        user_id) + "' AND date BETWEEN '" + first_date + "' AND '" + second_date + "'")
    answer = cursor.fetchall()
    db.close()
    return answer
