import os
import shutil
from pathlib import Path

from modules.connect_db import connect
from modules.new_db_logic import add_directory, get_user_id, del_directory, get_directory_by_id, update_name_directory


class FolderExistException(Exception):
    pass

class FolderNotFound(Exception):
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
            if len(os.listdir(path / Path(folder.name))) == 0:
                os.rmdir(path / Path(folder.name))
            else:
                shutil.rmtree(path / Path(folder.name))
            del_directory(engine, session, folder_id)
        else:
            raise FolderNotFound

    def update_folder_name(self, engine, session, user_name: str, folder_id: int, new_name: str):
        path = self.STORAGE_PATH / Path(user_name)
        folder = get_directory_by_id(engine, session, folder_id)
        if folder and folder.name_directory in os.listdir(path):
            os.rename(path / Path(folder.name_directory), path / Path(new_name))
            update_name_directory(engine, session, folder_id, new_name)
        else:
            raise FolderNotFound

    def create_file(self, folder_name: str, file_name: str):
        if folder_name in os.listdir(self.STORAGE_PATH):
            path = self.STORAGE_PATH / Path(folder_name)
            if file_name not in os.listdir(path):
                pass

    def update_file(self):
        pass

    def get_files(self):
        pass

    def del_files(self):
        pass
