from fastapi import HTTPException


def generate_bad_token_response():
    """Generates JSON response for cases when user sent a wrong token"""
    # return {'status': 'failed', 'error': {
    #     'code': 412,
    #     'description': 'Wrong token'
    # }}
    raise HTTPException(status_code=412, detail='Wrong token')


def generate_success_response():
    """Generates status-200 response"""
    return {'status': 'success', 'error': None}


def generate_username_inuse_response():
    """Generates response for cases when user is trying to use already a used login"""
    # return {'status': 'failed', 'error': {
    #     'code': 410,
    #     'description': 'The username already signed up'
    # }}
    raise HTTPException(status_code=410, detail='The username already signed up')


def generate_bad_authdata_response():
    """Returns data for cases when auth data is wrong """
    # return {'status': 'failed', 'error': {
    #     'code': 411,
    #     'description': 'Email or password is wrong'
    # }}
    raise HTTPException(status_code=411, detail='Email or password is wrong')


def generate_folder_exist_error():
    """Returns data for cases when folder exists"""
    # return {'success': 'false', 'error': {'code': 420, 'description': 'The folder already exists'}}
    raise HTTPException(status_code=400, detail='The folder already exists')

def generate_file_exist_error():
    """Returns data for cases when folder exists"""
    # return {'success': 'false', 'error': {'code': 420, 'description': 'The folder already exists'}}
    raise HTTPException(status_code=400, detail='The file already exists')

def generate_folder_not_found_error():
    """Returns data for cases when folder not found"""
    # return {'success': 'false', 'error': {'code': 421, 'description': 'The folder not found'}}
    raise HTTPException(status_code=421, detail='The folder not found')

def generate_file_not_found_error():
    """Returns data for cases when file not found"""
    raise HTTPException(status_code=400, detail='File not found')

def generate_download_failed_error():
    raise HTTPException(status_code=400, detail='Request exception. Check your url.')

def generate_success_directories(directories: list):
    """Generates response for reading directories"""
    return {'status': 'success', 'error': None, 'directories': directories}


def generate_success_regdata(name: str, token: str) -> dict:
    """Generates response for the successful registration"""
    return {'status': 'success', 'error': None, 'user_name': name, 'token': token}


def generate_success_wtoken(token: str) -> dict:
    """Generates 200-code response with the token"""
    return {'status': 'success', 'error': None, 'token': token}


def generate_success_wdata(data) -> dict:
    """Generates 200-code response with the data"""
    return {'status': 'success', 'error': None, 'data': data}
