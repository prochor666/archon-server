from archon import app, data, utils
from archon.models.users import users 
import json

def _users(data_pass: dict = {}) -> dict:
    _filter = utils.ark('filter', data_pass)
    _sort = utils.ark('sort', data_pass)
    
    if type(_filter) is str:
        data_pass['filter'] =  json.loads(_filter) if len(_filter) > 0 else {}

    if type(_sort) is str:
        data_pass['sort'] = json.loads(_sort) if len(_sort) > 0 else {}

    data_filter = utils.apply_filter(data_pass)
    u = users.load(data_filter['filter'], data_filter['sort']) 

    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No users",
        'type': type(u).__name__,
        'users': [],
        'data_filter': data_filter,
        'count': 0 if type(u) is not list or u == None else len(u)
    }

    if result['count'] > 0:
        result['status'] = True
        result['users'] = data.collect(u)
        result['message'] = f"Found users ({result['count']})"
    return result


def _load_one(id: str) -> dict:
    r = users.load_one(filter_data = {
        'id': id
    })

    result = {
        'status': False,
        'message': "No user",
        'type': type(r).__name__,
        'user': {},
    }

    if type(r).__name__ == 'dict':
        #r['_id'] = str(r['_id'])
        result['status'] = True
        result['user'] = data.collect_one(r)
        result['type'] = type(r).__name__
        result['message'] = f"Found user"
    return result


def _get_system_user(data_pass: dict = {}) -> dict:
    return users.system_user()


def _user_create(data_pass: dict = {}) -> dict:
    result = users.insert(data_pass)
    return result


def _user_modify(data_pass: dict = {}) -> dict:
    result = users.modify(data_pass)
    return result


def _user_delete(data_pass: dict = {}) -> dict:
    result = users.delete(data_pass)
    return result


def _user_activate(data_pass: dict = {}) -> dict:
    result = users.activate(data_pass)
    return result
