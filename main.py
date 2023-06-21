import secrets
import string

from fastapi import FastAPI
from pydantic import EmailStr

api = FastAPI()


@api.post("/sign_up")
def sign_up(user_name: str, user_email: EmailStr, password: str):
    token = generate_token()
    # TODO check existing user
    # TODO add user to the database
    return {'status': 'success', 'error': None, 'user_name': user_name, 'token': token}


@api.post('/sign_in')
def sign_in(user_email: EmailStr, password: str):
    # TODO check existing user
    # TODO check user_email and user password
    pass


@api.post("/upload_data")
def upload_data():
    pass


@api.get("/get_data")
def get_data():
    pass

def generate_token(length=16):
    characters = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(characters) for _ in range(length))
    return token