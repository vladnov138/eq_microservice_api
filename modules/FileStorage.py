import os
from pathlib import Path

from modules.new_db_logic import add_directory, get_user_id


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

    def create_folder(self, folder_name: str, user_name: str):
        path = self.STORAGE_PATH / Path(user_name)
        if folder_name not in os.listdir(path):
            user_id = get_user_id(user_name)
            os.makedirs(path / Path(folder_name))
            add_directory(int(user_id), folder_name)
        else:
            raise FolderExistException

    def delete_folder(self, name: str):
        if name in os.listdir(self.STORAGE_PATH):
            if len(os.listdir(self.STORAGE_PATH / Path(name))) == 0:
                os.rmdir(self.STORAGE_PATH / Path(name))
            else:
                # TODO Warn user about data
                pass
        else:
            raise FolderNotFound



    # def create_file(self, folder_name: str, file_name: str):
    #     if folder_name in os.listdir(self.STORAGE_PATH):
    #         path = self.STORAGE_PATH / Path(folder_name)
    #         if file_name not in os.listdir(path):
