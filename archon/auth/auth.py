from archon import app, data
from archon.models.users import users


def authorization_process(authorization: str, required = True) -> dict:

    result = {
        'status': False,
        'message': "Authorization failed",
        'data': {}
    }

    if required == True:
        if len(authorization) > 0:
            auth_token = extract_auth_token(
                authorization)

            result['message'] = "User found, secret check failed"

            if len(auth_token) > 63:
                user_data = login({'auth_token': auth_token})
                result['data'] = user_data
    else: 
        result['message'] = "No authorization required"
        result['status'] = True

    return result


def login(auth_token: str) -> dict:
    result = False

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
    }, exclude_keys = False)

    if type(user) is dict:
        return data.collect_one(user)

    return False
