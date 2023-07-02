import os
from datetime import datetime

from fastapi.testclient import TestClient

from ..crud import get_user_id, del_user, get_directories, del_directory, search_name_by_token, check_user, \
    get_directory_by_id
from ..database import clean_db
from ..main import app, engine, session, storage


class TestApp():
    client = TestClient(app)
    nickname = 'test_user123'
    email = 'test_user123@mail.ru'
    password = 'test_password123'
    token = None

    def test_sign_up(self):
        # if check_user(engine, session, self.nickname):
        #     del_user(engine, session, self.nickname)
        params = {'user_name': self.nickname,
                  'user_email': self.email,
                  'password': self.password}
        response = self.client.post('/sign_up', params=params)
        assert response.status_code == 200
        assert response.json()['token']
        response = self.client.post('/sign_up', params=params)
        assert response.status_code == 410
        assert response.json()['detail'] == 'The username already signed up'

    def test_sign_in(self):
        params = {'user_email': self.email,
                  'password': self.password}
        response = self.client.post('/sign_in', params=params)
        assert response.status_code == 200
        assert response.json()['token']
        params['password'] += '123'
        response = self.client.post('/sign_in', params=params)
        assert response.status_code == 411
        assert response.json()['detail'] == 'Email or password is wrong'

    def get_token(self):
        params = {'user_email': self.email,
                  'password': self.password}
        response = self.client.post('/sign_in', params=params)
        if response.status_code == 200:
            return response.json()['token']

    def check_token(self, url: str, params: dict):
        params['token'] += '123'
        response = self.client.post(url, params=params)
        assert response.status_code == 412
        assert response.json()['detail'] == 'Wrong token'

    def get_folder_id(self, token: str):
        response = self.client.post('/get_folders', params={'token': token, 'limit': 5})
        if response.status_code == 200:
            return response.json()['directories'][0]['id']

    def get_file_id(self, token):
        response = self.client.post('/get_data', params={'token': token, 'folder_id': self.get_folder_id(token),
                                                         'limit': 5})
        if response.status_code == 200 and len(response.json()['data']) > 0:
            return response.json()['data'][0]['id']

    def test_create_new_folder(self):
        token = self.get_token()
        dirs = get_directories(engine, session, get_user_id(engine, session,
                                                            search_name_by_token(engine, session, token)))
        # for dir in dirs:
        #     storage.delete_folder(engine, session, self.nickname, dir.id)
        params = {'token': token,
                  'name': 'test_folder'}
        response = self.client.post('/create_new_folder', params=params)
        assert response.status_code == 200
        assert response.json()['status'] == 'success'
        response = self.client.post('/create_new_folder', params=params)
        assert response.status_code == 420
        assert response.json()['detail'] == 'The folder already exists'
        self.check_token('/create_new_folder', params)

    def test_get_folder(self):
        params = {'token': self.get_token(),
                  'limit': 5}
        response = self.client.post('/get_folders', params=params)
        assert response.status_code == 200
        assert len(response.json()['directories']) == 1
        self.check_token('/get_folders', params)

    def test_rename_folder(self):
        token = self.get_token()
        id = self.get_folder_id(token)
        params = {'token': token,
                  'folder_id': int(id),
                  'new_name': 'new_test_folder'}
        response = self.client.put('/rename_folder', params=params)
        assert response.status_code == 200
        folder = get_directory_by_id(engine, session, id)
        assert folder.name_directory == 'new_test_folder'
        params['folder_id'] = -1
        response = self.client.put('/rename_folder', params=params)
        assert response.status_code == 421
        assert response.json()['detail'] == 'The folder not found'
        params['token'] += '123'
        response = self.client.put('rename_folder', params=params)
        assert response.status_code == 412
        assert response.json()['detail'] == 'Wrong token'

    def test_upload_data(self):
        token = self.get_token()
        folder_id = self.get_folder_id(token)
        data_id = self.get_file_id(token)
        # if data_id:
        #     storage.del_files(engine, session, data_id, folder_id,
        #                       search_name_by_token(engine, session, token))
        params = {'token': token,
                  'folder_id': folder_id,
                  'description': '2-10 minute TEC variations'}
        src = './app/test/dtec_2_10_01_17.h5'
        if 'test' in os.getcwd():
            src = './dtec_2_10_01_17.h5'
        with open(src, 'rb') as file:
            upload_file = {'file': file}
            response = self.client.post('/upload_data', params=params, files=upload_file)
            assert response.status_code == 200
            params['folder_id'] = -1
            response = self.client.post('/upload_data', params=params, files=upload_file)
            assert response.status_code == 421
            assert response.json()['detail'] == 'The folder not found'
            params['token'] += '123'
            response = self.client.post('upload_data', params=params, files=upload_file)
            assert response.status_code == 412
            assert response.json()['detail'] == 'Wrong token'

    def test_get_data(self):
        token = self.get_token()
        folder_id = self.get_folder_id(token)
        params = {'token': token,
                  'folder_id': folder_id}
        response = self.client.post('/get_data', params=params)
        assert response.status_code == 200
        assert len(response.json()['data']) == 1
        self.check_token('/get_data', params=params)

    def test_get_data_by_date(self):
        token = self.get_token()
        folder_id = self.get_folder_id(token)
        params = {'token': token,
                  'folder_id': folder_id,
                  # 'start_date': '2023-02-06 01:17:00',
                  'start_date': datetime(2023, 2, 6, 1, 17),
                  # 'finish_date': '2023-02-06 01:17:30'}
                  'finish_date': datetime(2023, 2, 6, 1, 17, 30)}
        response = self.client.post('/get_data_by_date', params=params)
        assert response.status_code == 200
        assert len(response.json()['data']) == 1
        self.check_token('/get_data_by_date', params=params)

    def test_delete_data(self):
        token = self.get_token()
        folder_id = self.get_folder_id(token)
        data_id = self.get_file_id(token)
        params = {'token': token,
                  'folder_id': folder_id,
                  'data_id': data_id}
        response = self.client.delete('/delete_data', params=params)
        assert response.status_code == 200
        response = self.client.delete('/delete_data', params=params)
        assert response.status_code == 400
        assert response.json()['detail'] == 'File not found'
        params['folder_id'] = -1
        response = self.client.delete('/delete_data', params=params)
        assert response.status_code == 421
        assert response.json()['detail'] == 'The folder not found'
        params['token'] += '123'
        response = self.client.delete('delete_data', params=params)
        assert response.status_code == 412
        assert response.json()['detail'] == 'Wrong token'

    def test_delete_folder(self):
        token = self.get_token()
        id = self.get_folder_id(token)
        params = {'token': token,
                  'folder_id': id}
        response = self.client.delete('delete_folder', params=params)
        assert response.status_code == 200
        response = self.client.delete('delete_folder', params=params)
        assert response.status_code == 421
        assert response.json()['detail'] == 'The folder not found'
        params['token'] += '123'
        response = self.client.delete('delete_folder', params=params)
        assert response.status_code == 412
        assert response.json()['detail'] == 'Wrong token'

    def test_del_db(self):
        clean_db(engine)
