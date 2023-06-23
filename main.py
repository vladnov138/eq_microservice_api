import os
import secrets
import string

import h5py
import uvicorn
from datetime import date, datetime

from fastapi import FastAPI, UploadFile, File
from pydantic import EmailStr

from modules.FileStorage import FileStorage
from modules.new_db_logic import check_user, add_user, authorization, search_by_token, search_by_email, get_user_id, \
    get_files, get_dates, update_file, del_file, add_file

from modules.responses import generate_success_response, generate_success_regdata, generate_bad_authdata_response, generate_bad_token_response, generate_username_inuse_response, generate_success_wtoken,  generate_success_wdata
from modules.security import generate_token


app = FastAPI()


@app.post("/sign_up")
async def sign_up(user_name: str, user_email: EmailStr, password: str) -> dict:
    token = generate_token()
    # TODO Fix check_user
    if check_user(user_name) > 0:
        return generate_bad_authdata_response()
    add_user(user_name, user_email, password, token)
    # os.mkdir(os.path.join(os.getcwd(), 'users_data', user_name))
    return generate_success_regdata(user_name, token)


@app.post('/sign_in')
async def sign_in(user_email: EmailStr, password: str) -> dict:
    if authorization(user_email, password) == 0:
        return generate_bad_authdata_response()
    token = search_by_email(user_email)
    return generate_success_wtoken(token)


@app.post('/create_new_folder')
def create_new_folder(token: str, name: str) -> dict:
    user_name = search_by_token(token)
    if user_name:
        storage = FileStorage()
        storage.create_folder(name)
        return generate_success_response()
    return generate_bad_token_response()


@app.post('/delete_folder')
def delete_folder(token: str, folder_id: str) -> dict:
    pass


@app.post('/get_folders')
def get_folders(token: str, limit: int) -> dict:
    pass


@app.post('/update_folder')
def update_folder(token: str, folder_id: str) -> dict:
    pass


@app.post("/upload_data")
async def upload_data(token: str, file: UploadFile = File(...)) -> dict:
    user_name = search_by_token(token)
    if user_name:
        filename = file.filename
        path = os.path.join(os.getcwd(), 'users_data', user_name, filename)
        with open(path, "wb") as f:
            f.write(await file.read())
        with h5py.File(path, "r") as f:
            date_objects = [datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f") for date_str
                            in list(f['data'].keys())]
        min_date = min(date_objects)
        max_date = max(date_objects)
        user_id = get_user_id(user_name)
        add_file(user_id, filename, min_date, max_date)
        return generate_success_response()
    return generate_bad_token_response()


@app.get("/get_last_data")
async def get_last_data(token: str, limit: int = 5) -> dict:
    user_name = search_by_token(token)
    if user_name:
        user_id = get_user_id(user_name)
        return generate_success_wdata(get_files(user_id, limit=limit))
    return generate_bad_token_response()


@app.post("/get_data_by_date")
async def get_data_by_date(token: str, start_date: date, finish_date: date) -> dict:
    user_name = search_by_token(token)
    if user_name:
        user_id = get_user_id(user_name)
        return generate_success_wdata(get_dates(user_id, start_date, finish_date))
    return generate_bad_token_response()


@app.post("/update_data")
async def update_data(token: str, data_id: int, file: UploadFile = File(...)) -> dict:
    user_name = search_by_token(token)
    if user_name:
        filename = file.filename
        path = os.path.join(os.getcwd(), 'users_data', user_name, filename)
        with open(path, "wb") as f:
            f.write(await file.read())
        user_id = get_user_id(user_name)
        update_file(data_id, filename)
        return generate_success_response()
    return generate_bad_token_response()


@app.post("/delete_data")
async def delete_data(token: str, data_id: int) -> dict:
    user_name = search_by_token(token)
    if user_name:
        user_id = get_user_id(user_name)
        del_file(data_id)
        return generate_success_response()
    return generate_bad_token_response()


def main():
    storage = FileStorage()
    storage.init_storage()
    uvicorn.run(f"{os.path.basename(__file__)[:-3]}:app", log_level="info")


if __name__ == '__main__':
    main()
