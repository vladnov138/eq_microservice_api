import modules.new_db_logic as logic
import modules.connect_db as connect
from datetime import datetime
import secrets

test_db = 'gg.db'


def del_user():
    pass


def test_add_user():
    token = secrets.token_hex(16)
    email = 'test' + token + '@mail.ru'
    nickname = 'test_user_' + token
    password = '123' + token
    engine, session = connect.connect(test_db)
    new_user = logic.add_user(engine, session, email, nickname, password, token)
    with session(autoflush=False, bind=engine) as db:
        users = db.query(connect.User).filter(connect.User.email == email,
                                              connect.User.nickname == nickname,
                                              connect.User.token == token).all()
    answer = new_user.id == users[0].id and len(users) == 1
    assert answer


def test_add_directory():
    token = secrets.token_hex(16)
    user_id = 1
    name_directory = 'test_directory_' + token
    engine, session = connect.connect(test_db)
    new_directory = logic.add_directory(engine, session, user_id, name_directory)
    with session(autoflush=False, bind=engine) as db:
        directories = db.query(connect.Directory).filter(connect.Directory.user_id == user_id,
                                                         connect.Directory.name_directory == name_directory).all()
    answer = new_directory.id == directories[0].id and len(directories) == 1
    assert answer


def test_add_file():
    token = secrets.token_hex(16)
    user_id = 1
    directory_id = 1
    file = 'test_file_' + token
    range_start = datetime.now()
    range_end = datetime.now()
    engine, session = connect.connect(test_db)
    new_file = logic.add_file(engine, session, user_id, directory_id, file, range_start, range_end)
    with session(autoflush=False, bind=engine) as db:
        files = db.query(connect.Uploaded_file).filter(connect.Uploaded_file.user_id == user_id,
                                                       connect.Uploaded_file.directory_id == directory_id,
                                                       connect.Uploaded_file.file == file,
                                                       connect.Uploaded_file.range_start == range_start,
                                                       connect.Uploaded_file.range_end == range_end).all()
    answer = new_file.id == files[0].id and len(files) == 1
    assert answer


def test_check_user():
    token = secrets.token_hex(16)
    email = 'test' + token + '@mail.ru'
    nickname = 'test_user_' + token
    password = '123' + token
    engine, session = connect.connect(test_db)
    logic.add_user(engine, session, email, nickname, password, token)
    assert logic.check_user(engine, session, nickname) == 1


def test_authorization():
    token = secrets.token_hex(16)
    email = 'test' + token + '@mail.ru'
    nickname = 'test_user_' + token
    password = '123' + token
    engine, session = connect.connect(test_db)
    logic.add_user(engine, session, email, nickname, password, token)
    assert logic.authorization(engine, session, email, password) == True


