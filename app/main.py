import base64
import os
import sys
from pathlib import Path

import numpy as np
import requests
import uvicorn
from datetime import date, datetime
from datetime import (datetime,
                      timedelta)

from fastapi import FastAPI, UploadFile, File, HTTPException
from loguru import logger
from matplotlib import pyplot as plt
from pydantic import EmailStr
from sqlalchemy import create_engine
from vesninlib.vesninlib import plot_maps, _UTC, plot_map, retrieve_data, plot_sites, retrieve_data_multiple_source, \
    get_dist_time, plot_distance_time, EPICENTERS, get_sites_coords, select_visible_sats_data, get_visible_sats_names, \
    select_sats_by_params, select_reoder_data, get_dtecs, calculate_distances_from_epicenter, plot_line

from app.modules.helper import plot_single_sat, fit_and_plot_distribution

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from app.modules.file_storage import FileStorage, FolderExistException, FolderNotFound, FileNotFound, FileExistException
from app.database import connect, create_bd
from app.crud import check_user, add_user, authorization, search_email_by_token, search_token_by_email, \
    get_user_id, \
    get_files, get_dates, update_file, del_file, add_file, add_directory, search_name_by_token, get_directories, \
    get_file, get_directory_by_id

from app.modules.responses import generate_success_response, generate_success_regdata, generate_bad_authdata_response, \
    generate_bad_token_response, generate_username_inuse_response, generate_success_wtoken, generate_success_wdata, \
    generate_folder_exist_error, generate_folder_not_found_error, generate_success_directories, \
    generate_file_not_found_error, generate_download_failed_error, generate_file_exist_error
from app.modules.security import generate_token

app = FastAPI()
storage = FileStorage()
engine, session = connect()
create_bd(engine)


@app.post("/sign_up")
def sign_up(user_name: str, user_email: EmailStr, password: str) -> dict:
    token = generate_token()
    logger.info("[Sign up] Received request to sign up a user")
    if check_user(engine, session, user_name):
        logger.error(f"[Sign up] User {user_name} is already signed up")
        return generate_username_inuse_response()
    add_user(engine, session, user_name, user_email, password, token)
    storage.init_user_storage(user_name)
    logger.info(f"[Sign up] User {user_name} signed up successfully")
    return generate_success_regdata(user_name, token)


@app.post('/sign_in')
def sign_in(user_email: EmailStr, password: str) -> dict:
    logger.info("[Sign in] Received request to sign in a user")
    if authorization(engine, session, user_email, password) == 0:
        return generate_bad_authdata_response()
    token = search_token_by_email(engine, session, user_email)
    return generate_success_wtoken(token)


@app.post('/create_new_folder')
def create_new_folder(token: str, name: str) -> dict:
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Create new folder] Received request to create new folder for user: {user_name}")
    if user_name:
        try:
            storage.create_folder(engine, session, name, user_name)
        except FolderExistException:
            logger.error(f"[Create new folder] The folder has been already created by: {user_name}")
            return generate_folder_exist_error()
        logger.info(f"[Create new folder] New folder was created by: {user_name}")
        return generate_success_response()
    logger.info(f"[Create new folder] Wrong token for user: {user_name}")
    return generate_bad_token_response()


@app.delete('/delete_folder')
def delete_folder(token: str, folder_id: int) -> dict:
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Delete folder] Received request to delete folder with id: {folder_id} for user: {user_name}")
    if user_name:
        try:
            storage.delete_folder(engine, session, user_name, folder_id)
            logger.info(f"[Delete folder] The folder with id: {folder_id} was successfully deleted by: {user_name}")
        except FolderNotFound:
            logger.error(f"[Delete folder] The folder with id: {folder_id} wasn't found for: {user_name}")
            return generate_folder_not_found_error()
        return generate_success_response()
    logger.info(f"[Delete folder] Wrong token for user: {user_name}")
    return generate_bad_token_response()


@app.post('/get_folders')
def get_folders(token: str, limit: int) -> dict:
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Get folders] Received request to get folders for user: {user_name}")
    if user_name:
        user_id = get_user_id(engine, session, user_name)
        directories = get_directories(engine, session, user_id)
        logger.info(f"[Get folders] Folders were given for user: {user_name}")
        return generate_success_directories(directories)
    logger.error(f"[Get folders] Wrong token for user: {user_name}")
    return generate_bad_token_response()


@app.put('/rename_folder')
def rename_folder(token: str, folder_id: int, new_name: str) -> dict:
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Rename folder] Received request to rename folder with id: {folder_id} to {new_name} "
                f"for user: {user_name}")
    if user_name:
        try:
            storage.update_folder_name(engine, session, user_name, folder_id, new_name)
        except FolderNotFound:
            logger.error(f"[Rename folder] Folder with id: {folder_id} not found for user: {user_name}")
            return generate_folder_not_found_error()
        logger.info(f"[Rename folder] Folder with id: {folder_id} was renamed to {new_name}: {user_name}")
        return generate_success_response()
    logger.error(f"[Rename folder] Wrong token for user: {user_name}")
    return generate_bad_token_response()


@app.post("/upload_data")
async def upload_data(token: str, folder_id: int, file: UploadFile, description: str) -> dict:
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Upload data] Received request to upload data to folder with id: {folder_id} "
                f"for user: {user_name}")
    if user_name:
        try:
            await storage.create_file(engine, session, user_name, folder_id, file, description)
        except FolderNotFound:
            logger.error(f"[Upload data] Folder with id: {folder_id} not found for user: {user_name}")
            return generate_folder_not_found_error()
        except FileExistException:
            logger.error(f"[Upload data] File in directory with id: {folder_id} is already exists "
                         f"for user: {user_name}")
            return generate_file_exist_error()
        logger.info(f"[Upload data] {file.filename} was uploaded to folder with id: {folder_id} "
                    f"by user: {user_name}")
        return generate_success_response()
    logger.error(f"[Upload data] Wrong token for user: {user_name}")
    return generate_bad_token_response()


@app.post("/upload_data_by_url")
async def upload_data_by_url(token: str, folder_id: int, download_url: str, description: str) -> dict:
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Upload data] Received request to upload data to folder with id: {folder_id} "
                f"for user: {user_name}")
    if user_name:
        try:
            response = requests.get(download_url)
            file = response.content
            await storage.create_file(engine, session, user_name, folder_id, file, description)
        except FolderNotFound:
            logger.error(f"[Upload data] Folder with id: {folder_id} not found for user: {user_name}")
            return generate_folder_not_found_error()
        except FileExistException:
            logger.error(f"[Upload data] File in directory with id: {folder_id} is already exists "
                         f"for user: {user_name}")
            return generate_file_exist_error()
        except requests.exceptions.RequestException:
            logger.error(f"[Upload data] Failed to download file from URL: {download_url}")
            return generate_download_failed_error()
        logger.info(f"[Upload data] File from URL: {download_url} was uploaded to folder with id: {folder_id} "
                    f"by user: {user_name}")
        return generate_success_response()
    logger.error(f"[Upload data] Wrong token for user: {user_name}")
    return generate_bad_token_response()


@app.post("/get_data")
async def get_data(token: str, folder_id: int, limit: int = 5) -> dict:
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Get data] Received request to get data from folder with id: {folder_id} "
                f"for user: {user_name}")
    if user_name:
        user_id = get_user_id(engine, session, user_name)
        logger.info(f"[Get data] Data were sent from folder with id: {folder_id} for user: {user_name}")
        return generate_success_wdata(get_files(engine, session, user_id, folder_id, limit=limit))
    logger.error(f"[Get data] Wrong token for user: {user_name}")
    return generate_bad_token_response()


@app.post("/get_data_by_date")
async def get_data_by_date(token: str, folder_id: int, start_date: datetime, finish_date: datetime) -> dict:
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Get data by date] Received request to get data by date from folder with id: {folder_id} "
                f"for user: {user_name}")
    if user_name:
        user_id = get_user_id(engine, session, user_name)
        logger.info(f"[Get data by date] Returned data by date between {start_date} and {finish_date} "
                    f"from folder with id: {folder_id} "
                    f"for user: {user_name}")
        return generate_success_wdata(get_dates(engine, session, user_id, start_date, finish_date))
    logger.error(f"[Get data by date] Wrong token for user: {user_name}")
    return generate_bad_token_response()


# @app.post("/update_data")
# async def update_data(token: str, data_id: int, folder_id: int, file_id: int, new_name: str,
#                       file: UploadFile) -> dict:
#     user_name = search_email_by_token(engine, session, token)
#     logger.info(f"[Update data] Received request to rename file with id: {file_id} to {new_name} from "
#                 f"folder with id: {folder_id} "
#                 f"for user: {user_name}")
#     if user_name:
#         filename = file.filename
#         path = os.path.join(os.getcwd(), 'users_data', user_name, filename)
#         with open(path, "wb") as f:
#             f.write(await file.read())
#         user_id = get_user_id(engine, session, user_name)
#         update_file(engine, session, data_id, filename)
#         return generate_success_response()
#     logger.error(f"[Update data] Wrong token for user: {user_name}")
#     return generate_bad_token_response()


@app.delete("/delete_data")
async def delete_data(token: str, folder_id: int, data_id: int) -> dict:
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Delete data] Received request to delete file with id: {data_id} by user: {user_name}")
    if user_name:
        try:
            # del_file(engine, session, data_id)
            storage.del_files(engine, session, data_id, folder_id, user_name)
        except FolderNotFound:
            logger.error(f"[Delete data] Folder with id {folder_id} not found")
            return generate_folder_not_found_error()
        except FileNotFound:
            logger.error(f"[Delete data] File with id {data_id} not found")
            return generate_file_not_found_error()
        logger.info(f"[Delete data] File with id {data_id} was successfully deleted")
        return generate_success_response()
    logger.error(f"[Delete data] Wrong token for user: {user_name}")
    return generate_bad_token_response()


@app.post('/handle_data/graphic1')
def handle_data_graphic1(token: str, folder_id: int, data_id_array: list, needed_datetime_array: list, title: str | None,
                lat_limits: list | None = None, lon_limits: list | None = None, color_limits: dict | None = None,
                scale: int | None = 1, ncols: int | None = 1):
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Handle data] Received request to handle files with id: [{data_id_array}] "
                f"from folder with id: {folder_id} by user: {user_name}")
    if user_name:
        folder = get_directory_by_id(engine, session, folder_id)
        result = []
        for data_id in data_id_array:
            files_product = {}
            data_file = get_file(engine, session, data_id)
            path = storage.get_directory_to_file(user_name, folder.name_directory, data_file.file)
            files_product[storage.get_directory_to_file(user_name, folder.name_directory, data_file.file)] \
                = data_file.description
            description = data_file.description if not title else title
            needed_datetime_array = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f') for t in needed_datetime_array]
            times = [t.replace(tzinfo=t.tzinfo or _UTC)
                     for t in needed_datetime_array]
            data = {description: retrieve_data(path, description)}
            savefig = storage.STORAGE_PATH / Path(user_name) / Path(folder.name_directory) / Path('test.png')
            if len(times) >= ncols:
                for i in range(0, len(times), ncols):
                    if not lat_limits or len(lat_limits) != 2:
                        lat_limits = (-90, 90)
                    if not lon_limits or len(lon_limits) != 2:
                        lon_limits = (-180, 180)
                    C_LIMITS = color_limits
                    if not color_limits:
                        C_LIMITS = {
                            'ROTI': [0, 0.5 * scale, 'TECu/min'],
                            '2-10 minute TEC variations': [-0.4 * scale, 0.4 * scale, 'TECu'],
                            '10-20 minute TEC variations': [-0.6 * scale, 0.6 * scale, 'TECu'],
                            '20-60 minute TEC variations': [-1 * scale, 1 * scale, 'TECu'],
                            'tec': [0, 50 * scale, 'TECu/min'],
                            'tec_adjusted': [0, 50 * scale, 'TECu'],
                        }

                    plot_map(times[i:i + ncols], data, description, clims= C_LIMITS, lat_limits=lat_limits,
                             lon_limits=lon_limits, savefig=f'{savefig}', ncols=ncols)
                    with open(savefig, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    result.append(encoded_string)
            else:
                raise HTTPException(status_code=400, detail='Error! Ncols < len(times)')
            with open(savefig, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return {'status': 'success', 'error': None, 'picture': encoded_string}
    logger.error(f"[Handle data] Wrong token for user: {user_name}")
    return generate_bad_token_response()


@app.post('/handle_data_region/graphic2')
def handle_data_graphic2(token: str, folder_id: int, data_id_array: list, title: str,
                         satellite: str | None = None, sites: list | None = None,
                         shift: float | None = 0.5):
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Handle data] Received request to handle files with id: [{data_id_array}] "
                f"from folder with id: {folder_id} by user: {user_name}")
    if user_name:
        if not sites:
            sites = ['mers', 'nico', 'bshm', 'csar', 'mrav', 'nzrt', 'hama',
                'hrmn', 'drag', 'kabr', 'katz', 'zkro', 'tmar', 'ista']
        if not satellite:
            satellite = 'G17'
        folder = get_directory_by_id(engine, session, folder_id)
        result = []
        for data_id in data_id_array:
            data_file = get_file(engine, session, data_id)
            path = storage.get_directory_to_file(user_name, folder.name_directory, data_file.file)
            plot_sites(path, satellite, sites, title, shift=shift)
            savefig = storage.STORAGE_PATH / Path(user_name) / Path(folder.name_directory) / Path('test.png')
            plt.savefig(savefig)
            with open(savefig, "rb") as image_file:
                result.append(base64.b64encode(image_file.read()).decode('utf-8'))
        return {'status': 'success', 'error': None, 'picture': result}
    logger.error(f"[Handle data] Wrong token for user: {user_name}")
    return generate_bad_token_response()


@app.post('/handle_data/graphic3')
def handle_data_graphic3(token: str, folder_id: int, data_id_array: list, title: str, time: str | None = '10:24',
                         plot_lines: list | None = None):
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Handle data] Received request to handle files with id: [{data_id_array}] "
                f"from folder with id: {folder_id} by user: {user_name}")
    if user_name:
        result = []
        folder = get_directory_by_id(engine, session, folder_id)
        data_file_paths = [storage.get_directory_to_file(user_name, folder.name_directory,
                                                         get_file(engine, session, data_id).file)
                           for data_id in data_id_array]
        data = retrieve_data_multiple_source(data_file_paths, title)
        x, y, c = get_dist_time(data, EPICENTERS[time])
        plot_distance_time(x, y, c, title, data=data)
        savefig = storage.STORAGE_PATH / Path(user_name) / Path(folder.name_directory) / Path('test.png')
        for p_line in plot_lines:
            style = 'solid'
            if len(p_line) == 3:
                style = p_line[2]
            elif len(p_line) != 2:
                raise HTTPException(status_code=400, detail=f"Invalid number of plot_lines. {len(p_line)}"
                                                            f"instead of 2 or 3")
            plot_line(p_line[0], datetime.strptime(p_line[1], '%Y-%m-%d %H:%M:%S.%f'), style=style)
        plt.savefig(savefig)
        with open(savefig, "rb") as image_file:
            result.append(base64.b64encode(image_file.read()).decode('utf-8'))
        return {'status': 'success', 'error': None, 'picture': result}
    logger.error(f"[Handle data] Wrong token for user: {user_name}")
    return generate_bad_token_response()


@app.post('/handle_data_region/graphic4')
def handle_data_graphic4(token: str, folder_id: int, data_id_array: list, title: str, needed_datetime: datetime,
                         satellite: str):
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Handle data] Received request to handle files with id: [{data_id_array}] "
                f"from folder with id: {folder_id} by user: {user_name}")
    if user_name:
        folder = get_directory_by_id(engine, session, folder_id)
        result = []
        for data_id in data_id_array:
            file = get_file(engine, session, data_id)
            path = storage.get_directory_to_file(user_name, folder.name_directory, file.file)
            coords = get_sites_coords(path,
                                      exclude_sites=['guru'])
            sites = [site for site in coords]
            data = select_visible_sats_data(path, sites, tcheck=needed_datetime)
            visible_sats = get_visible_sats_names(data)
            sats_count = select_sats_by_params(data, visible_sats, needed_datetime)
            _data = select_reoder_data(data, sats_count)
            dtecs = get_dtecs(_data, sort_type='max', sat=satellite, threshold=0.25, threshold_type='min')
            sites = []
            for d in dtecs[satellite]:
                sites.append(d['site'])
            savefig = storage.STORAGE_PATH / Path(user_name) / Path(folder.name_directory) / Path('test.png')
            plot_single_sat(dtecs, satellite, EPICENTERS['10:24'], 'dtec',
                            limits=(0, 1200),
                            shift=0.5, site_labels=True, namefile=savefig)
            with open(savefig, "rb") as image_file:
                result.append(base64.b64encode(image_file.read()).decode('utf-8'))
        return {'status': 'success', 'error': None, 'picture': result}
    logger.error(f"[Handle data] Wrong token for user: {user_name}")
    return generate_bad_token_response()


@app.post('/handle_data_region/graphic5')
def handle_data_graphic5(token: str, folder_id: int, data_id_range: list, needed_datetime: datetime):
    user_name = search_name_by_token(engine, session, token)
    logger.info(f"[Handle data] Received request to handle files with id: [{data_id_range}] "
                f"from folder with id: {folder_id} by user: {user_name}")
    if user_name:
        folder = get_directory_by_id(engine, session, folder_id)
        result = []
        for data_id in data_id_range:
            file = get_file(engine, session, data_id)
            path = storage.get_directory_to_file(user_name, folder.name_directory, file.file)
            coords = get_sites_coords(path, exclude_sites=['guru'])
            sites = [site for site in coords]
            data = select_visible_sats_data(path, sites, tcheck=needed_datetime)
            visible_sats = get_visible_sats_names(data)
            sats_count = select_sats_by_params(data, visible_sats, needed_datetime)
            _data = select_reoder_data(data, sats_count)
            sats = ['G17', 'G14', 'G24', 'E08']
            for start_time in [datetime(2023, 2, 6, 10, 35, 0) + timedelta(0, 30 * i) for i in range(1)]:
                deltas = list()
                dists = list()
                velocities = list()

                for sat in sats:
                    dtecs = get_dtecs(_data, sort_type='max', sat=sat, threshold=0.25, threshold_type='min')
                    elat = np.radians(EPICENTERS['10:24']['lat'])
                    elon = np.radians(EPICENTERS['10:24']['lon'])
                    calculate_distances_from_epicenter(dtecs, coords, sat, elat, elon)
                    for data in dtecs[sat]:
                        delta = (data['th_time'] - start_time) / timedelta(0, 1)
                        if delta == 0.0:
                            continue
                        velocity = data['distance'] / delta
                        if velocity < 0 or velocity > 4000:
                            continue
                        deltas.append(delta)
                        dists.append(data['distance'])
                        velocities.append(velocity)
                savefig = storage.STORAGE_PATH / Path(user_name) / Path(folder.name_directory) / Path('test.png')
                fit_and_plot_distribution(velocities, namefile=savefig)
                with open(savefig, "rb") as image_file:
                    result.append(base64.b64encode(image_file.read()).decode('utf-8'))
        return {'status': 'success', 'error': None, 'picture': result}
    logger.error(f"[Handle data] Wrong token for user: {user_name}")
    return generate_bad_token_response()


def main():
    storage.init_storage()
    engine, session = connect()
    create_bd(engine)
    uvicorn.run(f"{os.path.basename(__file__)[:-3]}:app", log_level="info")


if __name__ == '__main__':
    main()
