import os

import uvicorn
from datetime import date, datetime

from fastapi import FastAPI, UploadFile, File
from pydantic import EmailStr
from sqlalchemy import create_engine

from modules.FileStorage import FileStorage, FolderExistException, FolderNotFound
from modules.connect_db import connect, create_bd
from modules.new_db_logic import check_user, add_user, authorization, search_email_by_token, search_token_by_email, \
    get_user_id, \
    get_files, get_dates, update_file, del_file, add_file, add_directory, search_name_by_token, get_directories

from modules.responses import generate_success_response, generate_success_regdata, generate_bad_authdata_response, \
    generate_bad_token_response, generate_username_inuse_response, generate_success_wtoken, generate_success_wdata, \
    generate_folder_exist_error, generate_folder_not_found_error, generate_success_directories
from modules.security import generate_token


app = FastAPI()
storage = FileStorage()
connection_data = connect()
engine = connection_data[0]
session = connection_data[1]

@app.post("/sign_up")
def sign_up(user_name: str, user_email: EmailStr, password: str) -> dict:
    token = generate_token()
    if check_user(engine, session, user_name):
        return generate_username_inuse_response()
    add_user(engine, session, user_name, user_email, password, token)
    storage.init_user_storage(user_name)
    return generate_success_regdata(user_name, token)


@app.post('/sign_in')
def sign_in(user_email: EmailStr, password: str) -> dict:
    if authorization(engine, session, user_email, password) == 0:
        return generate_bad_authdata_response()
    token = search_token_by_email(engine, session, user_email)
    return generate_success_wtoken(token)


@app.post('/create_new_folder')
def create_new_folder(token: str, name: str) -> dict:
    user_name = search_name_by_token(engine, session, token)
    if user_name:
        try:
            storage.create_folder(engine, session, name, user_name)
        except FolderExistException:
            return generate_folder_exist_error()
        return generate_success_response()
    return generate_bad_token_response()


@app.post('/delete_folder')
def delete_folder(token: str, folder_id: int) -> dict:
    user_name = search_name_by_token(engine, session, token)
    if user_name:
        try:
            storage.delete_folder(engine, session, user_name, folder_id)
        except FolderNotFound:
            return generate_folder_not_found_error()
        return generate_success_response()
    return generate_bad_token_response()


@app.post('/get_folders')
def get_folders(token: str, limit: int) -> dict:
    user_name = search_name_by_token(engine, session, token)
    if user_name:
        user_id = get_user_id(engine, session, user_name)
        directories = get_directories(engine, session, user_id)
        return generate_success_directories(directories)
    return generate_bad_token_response()


@app.post('/rename_folder')
def rename_folder(token: str, folder_id: int, new_name: str) -> dict:
    user_name = search_name_by_token(engine, session, token)
    if user_name:
        try:
            storage.update_folder_name(engine, session, user_name, folder_id, new_name)
        except FolderExistException:
            return generate_folder_not_found_error()
        return generate_success_response()
    return generate_bad_token_response()


@app.post("/upload_data")
async def upload_data(token: str, folder_id: int, file: UploadFile = File(...)) -> dict:
    user_name = search_name_by_token(engine, session, token)
    if user_name:
        try:
            await storage.create_file(engine, session, user_name, folder_id, file)
        except FolderNotFound:
            return generate_folder_not_found_error()
        return generate_success_response()
    return generate_bad_token_response()


@app.get("/get_last_data")
async def get_last_data(token: str, limit: int = 5) -> dict:
    user_name = search_email_by_token(engine, session, token)
    if user_name:
        user_id = get_user_id(engine, session, user_name)
        return generate_success_wdata(get_files(user_id, limit=limit))
    return generate_bad_token_response()


@app.post("/get_data_by_date")
async def get_data_by_date(token: str, start_date: date, finish_date: date) -> dict:
    user_name = search_name_by_token(engine, session, token)
    if user_name:
        user_id = get_user_id(engine, session, user_name)
        return generate_success_wdata(get_dates(user_id, start_date, finish_date))
    return generate_bad_token_response()


@app.post("/update_data")
async def update_data(token: str, data_id: int, file: UploadFile = File(...)) -> dict:
    user_name = search_email_by_token(engine, session, token)
    if user_name:
        filename = file.filename
        path = os.path.join(os.getcwd(), 'users_data', user_name, filename)
        with open(path, "wb") as f:
            f.write(await file.read())
        user_id = get_user_id(engine, session, user_name)
        update_file(engine, session, data_id, filename)
        return generate_success_response()
    return generate_bad_token_response()


@app.post("/delete_data")
async def delete_data(token: str, data_id: int) -> dict:
    user_name = search_email_by_token(engine, session, token)
    if user_name:
        user_id = get_user_id(engine, session, user_name)
        del_file(engine, session, data_id)
        return generate_success_response()
    return generate_bad_token_response()


def main():
    storage.init_storage()
    create_bd(create_engine(f"sqlite:///../database/newdb.db"))
    uvicorn.run(f"{os.path.basename(__file__)[:-3]}:app", log_level="info")


if __name__ == '__main__':
    main()
