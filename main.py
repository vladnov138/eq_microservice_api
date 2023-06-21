import secrets
import string
from datetime import date

from fastapi import FastAPI
from pydantic import EmailStr

from bdLogic import check_user, add_user, authorization, search_by_token, search_by_email, get_user_id, add_file

app = FastAPI()


@api.post("/sign_up")
def sign_up(user_name: str, user_email: EmailStr, password: str):
    token = generate_token()
    if check_user(user_name) > 0:
        return {'status': 'failed', 'error': {
            'code': 410,
            'description': 'The username already signed up'
        }}
    add_user(user_name, user_email, password, token)
    os.mkdir(os.path.join(os.getcwd(), 'users_data', user_name))
    return {'status': 'success', 'error': None, 'user_name': user_name, 'token': token}


@api.post('/sign_in')
def sign_in(user_email: EmailStr, password: str):
    if authorization(user_email, password) == 0:
        return {'status': 'failed', 'error': {
            'code': 411,
            'description': 'Email or password is wrong'
        }}
    token = search_by_email(user_email)
    return {'status': 'success', 'error': None, 'token': token}


@app.post("/upload_data")
async def upload_data(token: str, file: UploadFile = File(...)):
    user_name = search_by_token(token)
    if user_name:
        filename = file.filename
        with open(os.path.join(os.getcwd(), 'users_data', user_name, filename), "wb") as f:
            f.write(await file.read())
        user_id = get_user_id(user_name)
        add_file(user_id, filename)
        return {'status': 'success', 'error': None}
    else:
        return {'status': 'failed', 'error': {
            'code': 412,
            'description': 'Wrong token'
        }}


@app.get("/get_last_data")
def get_last_data(token: str, num: int = 5):
    pass


@app.get("/get_data")
def get_data(token: str, start_date: date, finish_date: date):
    pass


def generate_token(length=16):
    characters = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(characters) for _ in range(length))
    return token