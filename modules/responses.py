from modules.db_logic import check_user, add_user, authorization, search_by_token, search_by_email, get_user_id, \
    add_file, \
    get_files, get_dates, update_file, del_file


def generate_bad_token_response():
    """Generates JSON response for cases when user sent a wrong token"""
    return {'status': 'failed', 'error': {
        'code': 412,
        'description': 'Wrong token'
    }}


def generate_success_response():
    """Generates status-200 response"""
    return {'status': 'success', 'error': None}


def generate_username_inuse_response():
    """Generates response for cases when user is trying to use already a used login"""
    return {'status': 'failed', 'error': {
        'code': 410,
        'description': 'The username already signed up'
    }}


def generate_bad_authdata_response():
    """Returns data for cases when auth data is wrong """
    return {'status': 'failed', 'error': {
        'code': 411,
        'description': 'Email or password is wrong'
    }}


def generate_success_regdata(name: str, token: str) -> dict:
    """Generates response for the successful registration"""
    return {'status': 'success', 'error': None, 'user_name': name, 'token': token}


def generate_success_wtoken(token: str) -> dict:
    """Generates 200-code response with the token"""
    return {'status': 'success', 'error': None, 'token': token}


def generate_success_wdata(data) -> dict:
    """Generates 200-code response with the data"""
    return {'status': 'success', 'error': None, 'data': data}
