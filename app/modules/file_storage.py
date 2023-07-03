import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import h5py
from fastapi import UploadFile

# sys.path.insert(1, '..')

from ..crud import add_directory, get_user_id, del_directory, get_directory_by_id, update_name_directory, \
    add_file, get_file, del_file


class FolderExistException(Exception):
    pass


class FileExistException(Exception):
    pass


class FolderNotFound(Exception):
    pass


class FileNotFound(Exception):
    pass


class FileStorage():
    __instance = None

    STORAGE_PATH = Path(os.getcwd()) / Path('users_data')
    CLEAN_AFTER_SECONDS = 24 * 3600 * 10
    TOKEN_LENGTH = 16

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(FileStorage, cls).__new__(cls)
        return cls.__instance

    def init_storage(self) -> bool:
        if not self.STORAGE_PATH.exists():
            os.makedirs(self.STORAGE_PATH)
            return True
        return False

    def init_user_storage(self, user_name: str) -> bool:
        path = self.STORAGE_PATH / Path(user_name)
        if not path.exists():
            os.makedirs(path)
            return True
        return False

    def create_folder(self, engine, session, folder_name: str, user_name: str):
        path = self.STORAGE_PATH / Path(user_name)
        if folder_name not in os.listdir(path):
            user_id = get_user_id(engine, session, user_name)
            os.makedirs(path / Path(folder_name))
            add_directory(engine, session, int(user_id), folder_name)
        else:
            raise FolderExistException

    def delete_folder(self, engine, session, user_name: str, folder_id: int):
        path = self.STORAGE_PATH / Path(user_name)
        folder = get_directory_by_id(engine, session, folder_id)
        if folder and folder.name_directory in os.listdir(path):
            folder_name = folder.name_directory
            if len(os.listdir(path / Path(folder_name))) == 0:
                os.rmdir(path / Path(folder_name))
            else:
                shutil.rmtree(path / Path(folder_name))
            del_directory(engine, session, folder_id)
        else:
            raise FolderNotFound

    def update_folder_name(self, engine, session, user_name: str, folder_id: int, new_name: str):
        path = self.STORAGE_PATH / Path(user_name)
        folder = get_directory_by_id(engine, session, folder_id)
        if folder and folder.name_directory in os.listdir(path):
            shutil.move(path / Path(folder.name_directory), path / Path(new_name))
            update_name_directory(engine, session, folder_id, new_name)
        else:
            raise FolderNotFound

    async def create_file(self, engine, session, user_name: str, folder_id: int, file: UploadFile,
                          description: str):
        user_id = get_user_id(engine, session, user_name)
        path = self.STORAGE_PATH / Path(user_name)
        folder = get_directory_by_id(engine, session, folder_id)
        if folder and folder.name_directory in os.listdir(path):
            path /= Path(folder.name_directory)
            if file.filename not in os.listdir(path):
                path /= Path(file.filename)
                with open(path, "wb") as f:
                    f.write(await file.read())
                try:
                    with h5py.File(path, "r") as f:
                        date_objects = [datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f') for date_str
                                        in list(f['data'].keys())]
                    min_date = min(date_objects)
                    max_date = max(date_objects)
                    add_file(engine, session, user_id, folder_id, file.filename, min_date, max_date,
                             description=description)
                except KeyError:
                    add_file(engine, session, user_id, folder_id, file.filename, None, None, description=description)
            else:
                raise FileExistException
        else:
            raise FolderNotFound

    def get_directory_to_file(self, user_name: str, folder_name: str, file_name: str):
        return self.STORAGE_PATH / Path(user_name) / Path(folder_name) / Path(file_name)

    # def update_file(self):
    #     pass

    def del_files(self, engine, session, data_id: int, folder_id: int, user_name: str):
        path = self.STORAGE_PATH / Path(user_name)
        folder = get_directory_by_id(engine, session, folder_id)
        if folder and folder.name_directory in os.listdir(path):
            file = get_file(engine, session, data_id)
            if file:
                path /= Path(folder.name_directory) / Path(file.file)
                os.remove(path)
                del_file(engine, session, data_id)
            else:
                raise FileNotFound
        else:
            raise FolderNotFound
