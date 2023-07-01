import os
from random import random

import app.crud as logic
import app.database as connect
from app.models import User, Uploaded_file, Directory
from datetime import datetime
import secrets

test_db = 'test.db'
# way = '/..' if 'app' in os.getcwd() else ''
way = '/..'


# print('WAY ', way, ' ', 'app' in os.getcwd())


def test_add_user():
    global way
    token = secrets.token_hex(16)
    email = 'test' + token + '@mail.ru'
    nickname = 'test_user_' + token
    password = '123' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_user_id = logic.add_user(engine, session, nickname, email, password, token)
    with session(autoflush=False, bind=engine) as db:
        users = db.query(User).filter(User.email == email,
                                      User.nickname == nickname,
                                      User.token == token).all()
    answer = new_user_id == users[0].id and len(users) == 1
    connect.clean_db(engine)
    assert answer


def test_add_directory():
    token = secrets.token_hex(16)
    user_id = 1
    name_directory = 'test_directory_' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_directory_id = logic.add_directory(engine, session, user_id, name_directory)
    with session(autoflush=False, bind=engine) as db:
        directories = db.query(Directory).filter(Directory.user_id == user_id,
                                                 Directory.name_directory == name_directory).all()
    answer = new_directory_id == directories[0].id and len(directories) == 1
    connect.clean_db(engine)
    assert answer


def test_add_file():
    token = secrets.token_hex(16)
    user_id = 1
    directory_id = 1
    file = 'test_file_' + token
    range_start = datetime.now()
    range_end = datetime.now()
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_file_id = logic.add_file(engine, session, user_id, directory_id, file, range_start, range_end)
    with session(autoflush=False, bind=engine) as db:
        files = db.query(Uploaded_file).filter(Uploaded_file.user_id == user_id,
                                               Uploaded_file.directory_id == directory_id,
                                               Uploaded_file.file == file,
                                               Uploaded_file.range_start == range_start,
                                               Uploaded_file.range_end == range_end).all()
    answer = new_file_id == files[0].id and len(files) == 1
    connect.clean_db(engine)
    assert answer


def test_check_user():
    token = secrets.token_hex(16)
    email = 'test' + token + '@mail.ru'
    nickname = 'test_user_' + token
    password = '123' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    logic.add_user(engine, session, nickname, email, password, token)
    answer = logic.check_user(engine, session, nickname) == 1
    connect.clean_db(engine)
    assert answer


def test_authorization():
    token = secrets.token_hex(16)
    email = 'test' + token + '@mail.ru'
    nickname = 'test_user_' + token
    password = '123' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    logic.add_user(engine, session, nickname, email, password, token)
    assert logic.authorization(engine, session, email, password) == 1

    assert logic.authorization(engine, session, 'email1242', password) == 0
    connect.clean_db(engine)


def test_search_email_by_token():
    token = secrets.token_hex(16)
    email = 'test' + token + '@mail.ru'
    nickname = 'test_user_' + token
    password = '123' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    logic.add_user(engine, session, nickname, email, password, token)
    assert logic.search_email_by_token(engine, session, token) == email
    assert not bool(logic.search_email_by_token(engine, session, ''))
    connect.clean_db(engine)


def test_search_name_by_token():
    token = secrets.token_hex(16)
    email = 'test' + token + '@mail.ru'
    nickname = 'test_user_' + token
    password = '123' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    logic.add_user(engine, session, nickname, email, password, token)
    assert logic.search_name_by_token(engine, session, token) == nickname
    assert not bool(logic.search_name_by_token(engine, session, ''))
    connect.clean_db(engine)


def test_search_token_by_email():
    token = secrets.token_hex(16)
    email = 'test' + token + '@mail.ru'
    nickname = 'test_user_' + token
    password = '123' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    logic.add_user(engine, session, nickname, email, password, token)
    assert logic.search_token_by_email(engine, session, email) == token
    assert not bool(logic.search_token_by_email(engine, session, ''))
    connect.clean_db(engine)


def test_get_user_id():
    token = secrets.token_hex(16)
    email = 'test' + token + '@mail.ru'
    nickname = 'test_user_' + token
    password = '123' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    user_id = logic.add_user(engine, session, nickname, email, password, token)
    assert logic.get_user_id(engine, session, nickname) == user_id
    assert not bool(logic.get_user_id(engine, session, ''))
    connect.clean_db(engine)


def test_get_files():
    token = secrets.token_hex(16)
    user_id = int(random() * 10000)
    directory_id = int(random() * 10000)
    file = 'test_file_' + token
    range_start = datetime.now()
    range_end = datetime.now()
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_file_id_1 = logic.add_file(engine, session, user_id, directory_id, file, range_start, range_end)
    new_file_id_2 = logic.add_file(engine, session, user_id, directory_id, file, range_start, range_end)
    request = logic.get_files(engine, session, user_id, directory_id)
    assert len(request) == 2 \
           and request[0].id == new_file_id_1 \
           and request[1].id == new_file_id_2
    connect.clean_db(engine)


def test_get_file():
    token = secrets.token_hex(16)
    user_id = int(random() * 10000)
    directory_id = int(random() * 10000)
    file = 'test_file_' + token
    range_start = datetime.now()
    range_end = datetime.now()
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_file_id = logic.add_file(engine, session, user_id, directory_id, file, range_start, range_end)
    new_file = logic.get_file(engine, session, new_file_id)
    assert new_file.id == new_file_id and new_file.user_id == user_id and new_file.file == file
    assert not bool(logic.get_file(engine, session, new_file_id+1))
    connect.clean_db(engine)


def test_get_directories():
    token = secrets.token_hex(16)
    user_id = int(random() * 10000)
    directory_name_1 = 'test_directory1_' + token
    directory_name_2 = 'test_directory2_' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_directory_id_1 = logic.add_directory(engine, session, user_id, directory_name_1)
    new_directory_id_2 = logic.add_directory(engine, session, user_id, directory_name_2)
    directories = logic.get_directories(engine, session, user_id)
    connect.clean_db(engine)
    assert len(directories) == 2
    assert directories[0].id == new_directory_id_1 and directories[1].id == new_directory_id_2


def test_get_directory_id_by_name():
    token = secrets.token_hex(16)
    user_id = int(random() * 10000)
    directory_name = 'test_directory_' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_directory_id = logic.add_directory(engine, session, user_id, directory_name)
    directory_id = logic.get_directory_id_by_name(engine, session, user_id, directory_name)
    assert directory_id == new_directory_id
    assert not bool(logic.get_directory_id_by_name(engine, session, user_id, ''))
    connect.clean_db(engine)


def test_get_directory_by_id():
    token = secrets.token_hex(16)
    user_id = int(random() * 10000)
    directory_name = 'test_directory_' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_directory_id = logic.add_directory(engine, session, user_id, directory_name)
    directory = logic.get_directory_by_id(engine, session, new_directory_id)
    connect.clean_db(engine)
    assert directory.name_directory == directory_name
    assert directory.user_id == user_id


def test_get_dates():
    token = secrets.token_hex(16)
    user_id = int(random() * 10000)
    directory_id = int(random() * 10000)
    file = 'test_file_' + token
    range_start = datetime(2002, 10, 6, 15, 29, 43, 79060)
    range_end = datetime(2002, 12, 6, 15, 29, 43, 79060)
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_file_id_1 = logic.add_file(engine, session, user_id, directory_id, file, range_start, range_end)
    token = secrets.token_hex(16)
    file = 'test_file_' + token
    range_start = datetime(2002, 3, 6, 15, 29, 43, 79060)
    range_end = datetime(2002, 7, 6, 15, 29, 43, 79060)
    date1 = datetime(2002, 1, 6, 15, 29, 43, 79060)
    date2 = datetime(2002, 12, 20, 15, 29, 43, 79060)
    new_file_id_2 = logic.add_file(engine, session, user_id, directory_id, file, range_start, range_end)
    request = logic.get_dates(engine, session, user_id, date1, date2)
    assert len(request) == 2
    connect.clean_db(engine)


def test_del_user():
    token = secrets.token_hex(16)
    email = 'test' + token + '@mail.ru'
    nickname = 'test_user_' + token
    password = '123' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    logic.add_user(engine, session, nickname, email, password, token)
    logic.del_user(engine, session, nickname)
    assert logic.check_user(engine, session, nickname) == False
    connect.clean_db(engine)


def test_del_file():
    token = secrets.token_hex(16)
    user_id = int(random() * 10000)
    directory_id = int(random() * 10000)
    file = 'test_file_' + token
    range_start = datetime.now()
    range_end = datetime.now()
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_file_id = logic.add_file(engine, session, user_id, directory_id, file, range_start, range_end)
    logic.del_file(engine, session, new_file_id)
    with session(autoflush=False, bind=engine) as db:
        file = db.query(Uploaded_file).filter(Uploaded_file.id == new_file_id).first()
    assert bool(file) == False
    connect.clean_db(engine)


def test_del_directory():
    token = secrets.token_hex(16)
    user_id = int(random() * 10000)
    directory_name = 'test_directory_' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_directory_id = logic.add_directory(engine, session, user_id, directory_name)
    logic.del_directory(engine, session, new_directory_id)
    directory = logic.get_directory_by_id(engine, session, new_directory_id)
    assert not bool(directory)
    connect.clean_db(engine)


def test_update_file():
    token = secrets.token_hex(16)
    user_id = int(random() * 10000)
    directory_id = int(random() * 10000)
    file = 'test_file_' + token
    range_start = datetime.now()
    range_end = datetime.now()
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_file_id = logic.add_file(engine, session, user_id, directory_id, file, range_start, range_end)
    new_name_file = token
    logic.update_file(engine, session, new_file_id, new_name_file)
    with session(autoflush=False, bind=engine) as db:
        file = db.query(Uploaded_file).filter(Uploaded_file.id == new_file_id).first()
    assert file.file == new_name_file
    connect.clean_db(engine)


def test_update_description_file():
    token = secrets.token_hex(16)
    user_id = int(random() * 10000)
    directory_id = int(random() * 10000)
    file = 'test_file_' + token
    range_start = datetime.now()
    range_end = datetime.now()
    description = 'test_description_' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_file_id = logic.add_file(engine, session, user_id, directory_id, file, range_start, range_end,
                                 description=description)
    new_description = '123'
    logic.update_description_file(engine, session, new_file_id, new_description)
    file = logic.get_file(engine, session, new_file_id)
    assert file.description != description
    assert file.description == new_description


def test_update_name_directory():
    token = secrets.token_hex(16)
    user_id = int(random() * 10000)
    directory_name = 'test_directory_' + token
    engine, session = connect.connect(test_db, way)
    connect.create_bd(engine)
    new_directory_id = logic.add_directory(engine, session, user_id, directory_name)
    new_name = 'new_name'
    logic.update_name_directory(engine, session, new_directory_id, new_name)
    directory = logic.get_directory_by_id(engine, session, new_directory_id)
    assert directory.name_directory != directory_name
    assert directory.name_directory == new_name
    connect.clean_db(engine)
