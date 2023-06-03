from archon import app, data
from archon.models.users import users


def authorization_process(endpoint: str, method: str, authorization: str) -> dict:

    result = {
        'message': "Authorization failed",
        'username': '',
        'role': '',
        'status': False
    }

    if endpoint in app.config['api']['rest'].keys() and \
        app.config['api']['rest'][endpoint]['authorized'] == True and \
        method in app.config['api']['rest'][endpoint]['methods']:

        if len(authorization) > 0:
            auth_token = extract_auth_token(
                authorization)

            if len(auth_token) > 63:
                login_obj = login({'auth_token': auth_token})
                return login_obj

    if endpoint in app.config['api']['rest'].keys() and \
        app.config['api']['rest'][endpoint]['authorized'] == False and \
        method in app.config['api']['rest'][endpoint]['methods']:

        result['message'] = "No authorization required"
        result['status'] = True

    return result


def login(data_pass: dict = {}) -> dict:
    result = {
        'message': "Token authorization failed",
        'username': '',
        'role': '',
        'status': False
    }

    if 'auth_token' in data_pass.keys():
        user_data = get_user_from_db(data_pass['auth_token'])

        if type(user_data) is dict:
            secret_key_check = users.hash_user({
                'email': user_data['email'],
                'salt':  user_data['salt'],
                'pwd': data_pass['auth_token']
            })

            result['message'] = "User found, secret check failed"

            if 'username' in user_data.keys() and 'pwd' in user_data.keys() and data_pass['auth_token'] == user_data['pwd'] and secret_key_check == user_data['secret']:
                result['message'] = "Authorization succeeded"
                result['username'] = user_data['username']
                result['role'] = user_data['role']
                result['email'] = user_data['email']
                result['_id'] = user_data['_id']
                result['status'] = True

    return result


def extract_auth_token(header: str) -> str:
    auth_token = ''
    prefix = app.config['authorization']['header_prefix']

    if header.startswith(prefix, 0, len(prefix)):
        auth_token = header[len(prefix):]

    return auth_token


def get_user_from_db(token: str) -> bool | dict:
    user = users.load_one({
        'pwd': token
    }, no_filter_pattern=True)

    if type(user) is dict:
        return data.collect_one(user)

    return False
