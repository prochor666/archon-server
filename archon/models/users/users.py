from bson.objectid import ObjectId
from archon import app, utils, data
from archon.auth import secret
from archon.mailer import mailer


def load(filter_data: dict, sort_data: list | None = None) -> list:
    finder = {
        'collection': 'users',
        'filter': filter_data,
        'sort': sort_data,
        'exclude': filter_user_pattern()
    }
    r = data.ex(finder)
    if type(r).__name__ == 'Cursor':  
        return list(r)
    else:
        return r


def load_one(filter_data: dict, exclude_keys: bool = True) -> dict:
    finder = {
        'collection': 'users',
        'filter': filter_data
    }
    if exclude_keys == True:
        finder['exclude'] = filter_user_pattern()
    r = data.one(finder)
    return r


def filter_user_pattern() -> dict:
    return {'secret': 0, 'pwd': 0, 'salt': 0}


def insert(user_data: dict) -> dict:
    result = validator(user_data)

    if result['status'] == True:

        user = user_model(user_data)
        users_collection = app.db['users']
        # users_collection.create_index("username", unique=True)
        # users_collection.create_index("email", unique=True)

        finder = load_one({
            '$or': [
                {'username': user['username']},
                {'email': user['email']}
            ]
        })

        if type(finder) is not dict:
            user['pwd'] = secret.token_urlsafe(64)
            user['salt'] = secret.token_rand(64)
            user['secret'] = hash_user(user)
            user['ulc'] = secret.token_urlsafe(32)
            user['pin'] = int(secret.pin(6))

            http_origin = ''
            if 'http_origin' in user_data.keys():
                http_origin = str(user_data.pop('http_origin', None))

            user['created_at'] = utils.now()
            user['creator'] = app.store['user']['data']['_id']

            users_collection.insert_one(user)

            html_message = mailer.assign_template(
                'register', {
                    'app_full_name': app.config['full_name'],
                    'app_name': app.config['name'],
                    'username': user['username'],
                    'pin': user['pin'],
                    'activation_link': activation_link(user, http_origin)
                })

            es = mailer.send(
                user['email'], f"{app.config['name']} - new account", html_message)
            result['status'] = True
            result['message'] = f"User {user['username']} created"
            result['email_status'] = es
        else:
            param_found = ''
            if finder['username'] == user['username']:
                param_found = f"with username {user['username']}"
            if len(param_found) == 0 and finder['email'] == user['email']:
                param_found = f"with email {user['email']}"

            result['status'] = False
            result['message'] = f"User {param_found} already exists"

    return result


def modify(user_data: dict) -> dict:
    result = validator(user_data)

    if 'id' not in user_data.keys():
        result['message'] = 'Need id for modify user'
        result['status'] = False

    if result['status'] == True:

        finder = load_one({
            '$and': [
                {
                    '$or': [
                        {'username': user_data['username']},
                        {'email': user_data['email']}
                    ],
                },
                {
                    '_id': {
                        '$ne': ObjectId(str(user_data['id']))
                    }
                }
            ]
        })

        modify_user = load_one({
            '_id': ObjectId(user_data['id'])
        }, exclude_keys = False)

        if type(finder) is not dict and type(modify_user) is dict:

            http_origin = ''
            if 'http_origin' in user_data.keys():
                http_origin = str(user_data.pop('http_origin', None))

            user = dict()
            user.update(modify_user)
            user.update(user_data)

            #print('Modified user', user)

            changed = utils.detect_object_changes([
                'username',
                'email',
                'firstname',
                'lastname',
                'role',
            ], modify_user, user)

            users_collection = app.db['users']

            # Email changed, need authorize new auth token
            if user['email'] != modify_user['email']:
                user['pwd'] = secret.token_urlsafe(64)
                user['salt'] = secret.token_rand(64)
                user['pin'] = int(secret.pin(6))
                user['ulc'] = secret.token_urlsafe(32)
                html_template = 'modify-pw'
            else:
                #user['pwd'] = modify_user['pwd']
                html_template = 'modify'

            user['secret'] = hash_user(user)
            user['updater'] = app.store['user']['data']['id']
            user['updated_at'] = utils.now()

            if 'created_at' not in modify_user:
                user['created_at'] = utils.now()

            if 'creator' not in modify_user:
                user['creator'] = app.store['user']['data']['id']

            user = user_model(user)
            users_collection.update_one(
                {'_id': ObjectId(user_data['id'])}, {'$set': user})

            if changed == True:

                html_message = mailer.assign_template(
                    html_template, {
                        'app_full_name': app.config['full_name'],
                        'app_name': app.config['name'],
                        'username': user['username'],
                        'pin': user['pin'],
                        'activation_link': activation_link(user, http_origin)
                    })


                es = mailer.send(
                    user['email'], f"{app.config['name']} - account updated", html_message)
                result['email_status'] = es

            result['status'] = True
            result['message'] = f"User {user['username']} modified"
            result['changed'] = changed
            result['email_status'] = False

        else:
            param_found = ''
            if type(finder) is dict and 'username' in finder.keys() and finder['username'] == user_data['username']:
                param_found = f"with username {user_data['username']}"
            if len(param_found) == 0 and type(finder) is dict and 'email' in finder.keys() and finder['email'] == user_data['email']:
                param_found = f"with email {user_data['email']}"

            result['status'] = False
            result['message'] = f"User {param_found} already exists"

    return result


def recover(unifield: str, http_origin: str = '', soft: bool = True) -> dict:
    result = {
        'message': "User not found",
        'status': False,
        'login': unifield,
        'recovery_type': "soft" if soft == True else "full"
    }

    user = load_one({
        '$or': [
            {'username': unifield},
            {'email': unifield}
        ]
    }, exclude_keys = False)

    if type(user) is dict:

        result['message'] = f"Found user {user['username']}"
        result['status'] = True
        html_template = 'soft-recovery'

        user['pin'] = int(secret.pin(6))
        user['ulc'] = secret.token_urlsafe(32)

        new_activation_link = activation_link(user, http_origin)
        subject_suffix = "account activation"

        if app.mode == 'cli':
            result['pin'] = user['pin']
            result['ulc'] = user['ulc']
            result['activation_link'] = new_activation_link

        if soft == False:
            user['pwd'] = secret.token_urlsafe(64)
            user['salt'] = secret.token_rand(64)
            user['secret'] = hash_user(user)
            html_template = 'full-recovery'
            subject_suffix = "account recovery"

        users_collection = app.db['users']
        user['updated_at'] = utils.now()

        users_collection.update_one({'_id': ObjectId(user['_id'])}, {'$set': user})

        html_message = mailer.assign_template(
            html_template, {
                'app_full_name': app.config['full_name'],
                'app_name': app.config['name'],
                'username': user['username'],
                'pin': user['pin'],
                'activation_link': new_activation_link
            })

        es = mailer.send(
            user['email'], f"{app.config['name']} - {subject_suffix}", html_message)
        result['email_status'] = es

    return result


def activate(user_data: dict) -> dict:
    
    if 'pin' in user_data.keys() and len(user_data['pin']) > 0:
        user_data['pin'] = int(user_data['pin'])

    ulc = utils.eval_key('ulc', user_data)
    pin = utils.eval_key('pin', user_data, 'int')

    # print('ULC:', ulc)
    # print('PIN:',pin)

    user = load_one({
        '$and': [
            { 'ulc': ulc },
            { 'pin': pin }
        ]
    }, exclude_keys = False)

    result = {
        'message': "Invalid activation",
        'status': False,
        'ulc': ulc,
        'pin': pin,
    }

    if type(user) is dict:
        result['status'] = True
        result['message'] = "Valid activation"
        result['username'] = user['username']
        result['role'] = user['role']
        result['pwd'] = user['pwd']

    return result


def activation_link(user_data: dict, http_origin: str = '') -> str:
    link = ""

    if int(user_data['pin']) > 99999:
        client_url = compose_client_url(http_origin)
        link = f"{client_url}/activate/?ulc={str(user_data['ulc'])}&pin={str(user_data['pin'])}"

    return link


def compose_client_url(http_origin: str = '') -> str:
    if len(http_origin) > 0 and http_origin.startswith(('http://', 'https://')):
        if http_origin.endswith('/'):
            return http_origin[:-1]

        return http_origin

    protocol = "http"
    if app.config['https'] == True:
        protocol = "https"

    port_mask = str(app.config['mask_http_port'])
    if port_mask in ["80", "443"]:
        port = ""
    else:
        port = f":{port_mask}"

    link = f"{protocol}://{app.config['mask_http_origin']}{port}"

    return link


def delete(user_data: dict) -> dict:
    result = {
        'status': False,
        'message': 'Need id to delete user',
        'user_data': user_data
    }

    if 'id' in user_data.keys():
        users_collection = app.db['users']
        r = users_collection.delete_one({'_id': ObjectId(user_data['id'])})
        result['delete_status'] = r.deleted_count
        result['status'] = False if r.deleted_count == 0 else True
        result['message'] = 'User delete error' if r.deleted_count == 0 else 'User deleted'

    return result


def validator(user_data: dict) -> dict:
    result = {
        'status': False,
        'message': "Data error",
    }

    if 'email' in user_data.keys() and 'username' in user_data.keys():

        if type(user_data['email']) != str:
            result['message'] = "Enter valid email address"
            return result

        email_validation = mailer.check_email(user_data['email'])
        if not email_validation['status']:
            result['message'] = f"Email '{user_data['email']}' is invalid. {email_validation['description']}"
            return result

        if type(user_data['username']) != str:
            result['message'] = "Enter valid username"
            return result

        elif not utils.is_username(user_data['username']):
            result['message'] = f"{user_data['username']} is not a valid username. Only aplhanumeric and spaces are allowed"
            return result

        result['message'] = 'Ok'
        result['status'] = True

    return result


def system_user() -> dict:
    finder = load_one({
        'username': 'system'
    })

    if type(finder) is not dict:
        create_system_user()

        finder = load_one({
            'username': 'system'
        })

    return data.collect_one(finder)


def create_system_user() -> dict:

    user = user_model({
        'username': 'system',
        'firstname': 'System',
        'lastname': 'User',
        'role': 'admin',
        'email': 'noreply@local.none',
        'created_at': utils.now()
    })

    users_collection = app.db['users']
    users_collection.create_index("username", unique=True)
    users_collection.create_index("email", unique=True)

    user['pwd'] = 'system'
    user['salt'] = secret.token_rand(64)
    user['secret'] = hash_user(user)
    user['ulc'] = ''
    user['pin'] = 0

    users_collection.insert_one(user)

    return user


def user_model(user_data: dict) -> dict:

    user = {
        'username': utils.eval_key('username', user_data),
        'email': utils.eval_key('email', user_data),
        'firstname': utils.eval_key('firstname', user_data),
        'lastname': utils.eval_key('lastname', user_data),
        'meta': utils.eval_key('meta', user_data, 'dict'),
        'settings': utils.eval_key('settings', user_data, 'dict'),
        'role': utils.eval_key('role', user_data),
        'pin': utils.eval_key('pin', user_data, 'int'),
        'pwd': utils.eval_key('pwd', user_data),
        'salt': utils.eval_key('salt', user_data),
        'secret': utils.eval_key('secret', user_data),
        'ulc': utils.eval_key('ulc', user_data),
        'creator': utils.eval_key('creator', user_data),
        'updater': utils.eval_key('updater', user_data),
        'created_at': utils.eval_key('created_at', user_data),
        'updated_at': utils.eval_key('updated_at', user_data),
    }

    return user


def hash_user(user_data: dict) -> str | bool:
    secret_key = secret.create_secret({
        'email': user_data['email'],
        'salt': user_data['salt'],
        'pwd': user_data['pwd']})
    return secret_key
