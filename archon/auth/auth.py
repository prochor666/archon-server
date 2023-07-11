from archon import app, data, utils
from archon.models.users import users


def authorization_process(token: str = '', required = True) -> dict:

    result = {
        'status': False,
        'message': "Authorization failed",
        'token': token,
        'data': {}
    }

    if required == True:
        if len(token) > 0:
            auth_token = extract_auth_token(token)
            #print('Auth token', auth_token)
            result['token'] = auth_token
            user_data = login(auth_token = auth_token)
            result['message'] = "Token found, secret check failed"

            if (utils.ark(user_data, 'status', False) == True):
                result['data'] = user_data
                result['message'] = "User found, secret check is fine"
                result['status'] = True
    else: 
        result['message'] = "No authorization required"
        result['status'] = True

    return result


def login(auth_token: str) -> dict:
    result = {}

    user_data = get_user_from_db(auth_token)

    if type(user_data) is dict:
        secret_key_check = users.hash_user({
            'email': user_data['email'],
            'salt':  user_data['salt'],
            'pwd': auth_token
        })

        if 'username' in user_data.keys() and 'pwd' in user_data.keys() and auth_token == user_data['pwd'] and secret_key_check == user_data['secret']:
            result['message'] = "Authorization succeeded"
            result['username'] = user_data['username']
            result['role'] = user_data['role']
            result['email'] = user_data['email']
            result['id'] = user_data['_id']
            result['status'] = True

    return result


def extract_auth_token(header: str) -> str:
    auth_token = header
    prefix = app.config['authorization']['header_prefix']
    if len(prefix) > 0 and header.startswith(prefix, 0, len(prefix)):
        auth_token = header[len(prefix):]
    return auth_token


def get_user_from_db(token: str) -> bool | dict:
    user = users.load_one({
        'pwd': token
    }, exclude_keys = False)

    if type(user) is dict:
        return data.collect_one(user)

    return False
