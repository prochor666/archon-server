import json
import importlib.util
from archon import data, utils
from archon.models.notifications import notifications
from archon.models.servers import servers
from archon.models.scripts import scripts
from archon.models.sites import sites
from archon.models.items import items
from archon.models.users import users
from archon.network import monitoring


# Item modifiers and listings
def _items(data_pass: dict = {}) -> dict:
    _filter = utils.ark(data_pass, 'filter')
    _sort = utils.ark(data_pass, 'sort')

    if type(_filter) is str:
        data_pass['filter'] =  json.loads(_filter) if len(_filter) > 0 else {}

    if type(_sort) is str:
        data_pass['sort'] = json.loads(_sort) if len(_sort) > 0 else {}

    data_filter = utils.apply_filter(data_pass)
    u = items.load(
        data_filter['filter'], data_filter['sort'], data_filter['exclude'])

    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No items",
        'count': 0 if type(u) is not list or u == None else len(u),
        'items': [],
    }
    if result['count'] > 0:
        result['status'] = True
        result['message'] = f"Found items: {result['count']}"
        result['items'] = data.collect(u)

    return result


def _item_one(id: str) -> dict:
    r = items.load_one(filter_data = {
        'id': id
    })

    result = {
        'status': False,
        'message': "No item",
        'item': {},
    }

    if type(r).__name__ == 'dict':
        #r['_id'] = str(r['_id'])
        result['status'] = True
        result['item'] = data.collect_one(r)
        result['message'] = f"Found item"
    return result


def _item_create(data_pass: dict = {}) -> dict:
    result = items.insert(data_pass)
    return result


def _item_modify(data_pass: dict = {}) -> dict:
    result = items.modify(data_pass)
    return result


def _item_delete(data_pass: dict = {}) -> dict:
    result = items.delete(data_pass)
    return result


# Server modifiers and listings
def _servers(data_pass: dict = {}) -> dict:
    _filter = utils.ark(data_pass, 'filter')
    _sort = utils.ark(data_pass, 'sort')
    
    if type(_filter) is str:
        data_pass['filter'] =  json.loads(_filter) if len(_filter) > 0 else {}

    if type(_sort) is str:
        data_pass['sort'] = json.loads(_sort) if len(_sort) > 0 else {}
        
    data_filter = utils.apply_filter(data_pass)
    u = servers.load(
        data_filter['filter'], data_filter['sort'], data_filter['exclude'])

    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No servers",
        'count': 0 if type(u) is not list or u == None else len(u),
        'servers': [],
    }
    
    if result['count'] > 0:
        result['status'] = True
        result['message'] = f"Found servers: {result['count']}"
        result['servers'] = data.collect(u)

    return result


def _server_one(id: str) -> dict:
    r = servers.load_one(filter_data = {
        'id': id
    })

    result = {
        'status': False,
        'message': "No server",
        'server': {},
    }

    if type(r).__name__ == 'dict':
        #r['_id'] = str(r['_id'])
        result['status'] = True
        result['server'] = data.collect_one(r)
        result['message'] = f"Found server"
    return result


def _server_create(data_pass: dict = {}) -> dict:
    result = servers.insert(data_pass)
    return result


def _server_modify(data_pass: dict = {}) -> dict:
    result = servers.modify(data_pass)
    return result


def _server_delete(data_pass: dict = {}) -> dict:
    result = servers.delete(data_pass)
    return result


# Script modifiers and listings
def _scripts(data_pass: dict = {}) -> dict:
    _filter = utils.ark(data_pass, 'filter')
    _sort = utils.ark(data_pass, 'sort')

    if type(_filter) is str:
        data_pass['filter'] =  json.loads(_filter) if len(_filter) > 0 else {}

    if type(_sort) is str:
        data_pass['sort'] = json.loads(_sort) if len(_sort) > 0 else {}

    data_filter = utils.apply_filter(data_pass)
    u = scripts.load(
        data_filter['filter'], data_filter['sort'], data_filter['exclude'])

    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No scripts",
        'count': 0 if type(u) is not list or u == None else len(u),
        'scripts': [],
    }
    if result['count'] > 0:
        result['status'] = True
        result['message'] = f"Found scripts: {result['count']}"
        result['scripts'] = data.collect(u)

    return result


def _script_one(id: str) -> dict:
    r = scripts.load_one(filter_data = {
        'id': id
    })

    result = {
        'status': False,
        'message': "No script",
        'script': {},
    }

    if type(r).__name__ == 'dict':
        #r['_id'] = str(r['_id'])
        result['status'] = True
        result['script'] = data.collect_one(r)
        result['message'] = f"Found script"
    return result


def _script_create(data_pass: dict = {}) -> dict:
    result = scripts.insert(data_pass)
    return result


def _script_modify(data_pass: dict = {}) -> dict:
    result = scripts.modify(data_pass)
    return result


def _script_delete(data_pass: dict = {}) -> dict:
    result = scripts.delete(data_pass)
    return result


# Site modifiers and listings
def _sites(data_pass: dict = {}) -> dict:
    _filter = utils.ark(data_pass, 'filter')
    _sort = utils.ark(data_pass, 'sort')

    if type(_filter) is str:
        data_pass['filter'] =  json.loads(_filter) if len(_filter) > 0 else {}

    if type(_sort) is str:
        data_pass['sort'] = json.loads(_sort) if len(_sort) > 0 else {}

    data_filter = utils.apply_filter(data_pass)
    u = sites.load(
        data_filter['filter'], data_filter['sort'], data_filter['exclude'])

    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No sites",
        'count': 0 if type(u) is not list or u == None else len(u),
        'sites': [],
    }
    if result['count'] > 0:
        result['status'] = True
        result['message'] = f"Found sites: {result['count']}"

        _sites = data.collect(u)
        sites_collection = []
        # Map servers and scripts, to be more complex
        for site_data in _sites:
            site_data['server'] = data.collect_one(
                servers.load_one({'id': site_data['server_id']}))
            site_data['script'] = data.collect_one(
                scripts.load_one({'id': site_data['script_id']}))
            sites_collection.append(site_data)

        result['sites'] = sites

    return result


def _site_one(id: str) -> dict:
    r = sites.load_one(filter_data = {
        'id': id
    })

    result = {
        'status': False,
        'message': "No site",
        'site': {},
    }

    if type(r).__name__ == 'dict':
        #r['_id'] = str(r['_id'])
        result['status'] = True
        result['site'] = data.collect_one(r)
        result['message'] = f"Found site"
    return result


def _site_create(data_pass: dict = {}) -> dict:
    result = sites.insert(data_pass)
    return result


def _site_modify(data_pass: dict = {}) -> dict:
    result = sites.modify(data_pass)
    return result


def _site_delete(data_pass: dict = {}) -> dict:
    result = sites.delete(data_pass)
    return result


# Search
def _search(data_pass: dict) -> dict:
    if type(data_pass) is dict and 'search' in data_pass:
        utils.index_eval()
        user_exclude = users.filter_user_pattern()
        user_exclude.update({'pin': 0, 'ulc': 0})

        user_collection = data.ex({
            'collection': 'users',
            'filter': {
                '$or': [
                    {'username': {
                        "$regex": f"{data_pass['search']}", "$options": "i"}},
                    {'email': {
                        "$regex": f"{data_pass['search']}", "$options": "i"}},
                    {'firstname': {
                        "$regex": f"{data_pass['search']}", "$options": "i"}},
                    {'lastname': {
                        "$regex": f"{data_pass['search']}", "$options": "i"}}
                ]
            },
            'exclude': user_exclude
        })

        server_collection = data.ex({
            'collection': 'servers',
            'filter': {
                '$or': [
                    {'name': {"$regex": f"{data_pass['search']}", "$options": "i"}},
                    {'ipv4': {"$regex": f"{data_pass['search']}", "$options": "i"}},
                    {'ipv6': {"$regex": f"{data_pass['search']}", "$options": "i"}}
                ]
            }
        })

        site_collection = data.ex({
            'collection': 'sites',
            'filter': {
                '$or': [
                    {'name': {
                        "$regex": f"{data_pass['search']}", "$options": "i"}},
                    {'domain': {
                        "$regex": f"{data_pass['search']}", "$options": "i"}},
                    {'dev_domain': {
                        "$regex": f"{data_pass['search']}", "$options": "i"}}
                ]
            }
        })

        script_collection = data.ex({
            'collection': 'scripts',
            'filter': {
                '$or': [
                    {'name': {
                        "$regex": f"{data_pass['search']}", "$options": "i"}}
                ]
            },
            'exclude': {
                "content": 0
            }
        })

        device_collection = data.ex({
            'collection': 'devices',
            'filter': {
                '$or': [
                    {'name': {
                        "$regex": f"{data_pass['search']}", "$options": "i"}}
                ]
            },
            'exclude': {
                "content": 0
            }
        })

        item_collection = data.ex({
            'collection': 'items',
            'filter': {
                '$or': [
                    {'name': {
                        "$regex": f"{data_pass['search']}", "$options": "i"}}
                ]
            },
            'exclude': {
                "content": 0
            }
        })

        return {
            'search_term': data_pass['search'],
            'users': data.collect(user_collection),
            'servers': data.collect(server_collection),
            'sites': data.collect(site_collection),
            'scripts': data.collect(script_collection),
            'devices': data.collect(device_collection),
            'items': data.collect(item_collection),
        }

    return {}


# Notifications
def _notifications(data_pass: dict = {}) -> dict:
    _filter = utils.ark(data_pass, 'filter')
    _sort = utils.ark(data_pass, 'sort')
    data_pass = {
        'filter': json.loads(_filter) if len(_filter) > 0 else {},
        'sort': json.loads(_sort) if len(_sort) > 0 else {}
    }
    data_filter = utils.apply_filter(data_pass)
    u = notifications.load(data_filter['filter'], data_filter['sort'], data_filter['exclude'])

    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No servers",
        'notifications': [],
        'count': 0 if type(u) is str or u == None else u.count() # type: ignore
    }
    if result['count'] > 0:
        result['status'] = True
        result['message'] = f"Found notifications: {result['count']}"
        result['notifications'] = data.collect(u)

    return result