from archon import app, data, utils
from archon.models.users import users 


def _users(data_pass: dict = {}) -> dict:

    data_filter = utils.apply_filter(data_pass)
    u = users.load(data_filter['filter'], data_filter['sort']) 

    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No users",
        'users': [],
        'count': 0 if type(u) is str or u == None else u.count() # type: ignore
    }
    if result['count'] > 0:
        result['status'] = True

        if app.mode == 'http':
            for user in u:
                if user['username'] == 'system': # type: ignore
                    result['count'] = result['count'] - 1
                else:
                    result['users'].append(data.collect_one(user))
        else:
            result['users'] = data.collect(u)

        result['message'] = f"Found users: {result['count']}"

    return result


def _get_system_user(data_pass: dict = {}) -> dict:
    return users.system_user()


def _create_user(data_pass: dict = {}) -> dict:
    result = users.insert(data_pass)
    return result


def _modify_user(data_pass: dict = {}) -> dict:
    result = users.modify(data_pass)
    return result


def _delete_user(data_pass: dict = {}) -> dict:
    result = users.delete(data_pass)
    return result


def _activate_user(data_pass: dict = {}) -> dict:
    result = users.activate(data_pass)
    return result
