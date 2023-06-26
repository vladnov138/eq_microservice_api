import os
import shutil
from pathlib import Path

from modules.connect_db import connect
from modules.new_db_logic import add_directory, get_user_id, del_directory


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

    def create_folder(self, folder_name: str, user_name: str):
        path = self.STORAGE_PATH / Path(user_name)
        if folder_name not in os.listdir(path):
            user_id = get_user_id(user_name)
            os.makedirs(path / Path(folder_name))
            con = connect()
            add_directory(con[0], con[1], int(user_id), folder_name)
        else:
            raise FolderExistException

    def delete_folder(self, user_name: str, folder_name: str):
        path = self.STORAGE_PATH / Path(user_name)
        if folder_name in os.listdir(path):
            user_id = get_user_id(user_name)
            if len(os.listdir(path / Path(folder_name))) == 0:
                os.rmdir(path / Path(folder_name))
            else:
                shutil.rmtree(path / Path(folder_name))
            con = connect()
            #TODO id
            del_directory(con[0], con[1], folder_name)
        else:
            raise FolderNotFound

    def get_folders(self):
        pass

    def update_folder_name(self):
        pass

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
