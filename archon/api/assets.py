import json
import importlib.util
from archon import data, utils
from archon.models.notifications import notifications
from archon.models.servers import servers
from archon.models.scripts import scripts
from archon.models.sites import sites
from archon.models import items
from archon.network import monitoring


# Server modifiers and listings
def _servers(data_pass: dict = {}) -> dict:

    data_filter = utils.apply_filter(data_pass)
    u = servers.load(
        data_filter['filter'], data_filter['sort'], data_filter['exclude'])

    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No servers",
        'servers': [],
        'count': 0 if type(u) is str or u == None else u.count() # type: ignore
    }
    if result['count'] > 0:
        result['status'] = True
        result['message'] = f"Found servers: {result['count']}"
        result['servers'] = data.collect(u)

    return result


def _create_server(data_pass: dict = {}) -> dict:
    result = servers.insert(data_pass)
    return result


def _modify_server(data_pass: dict = {}) -> dict:
    result = servers.modify(data_pass)
    return result


def _delete_server(data_pass: dict = {}) -> dict:
    result = servers.delete(data_pass)
    return result


# Script modifiers and listings
def _scripts(data_pass: dict = {}) -> dict:

    data_filter = utils.apply_filter(data_pass)
    u = scripts.load(
        data_filter['filter'], data_filter['sort'], data_filter['exclude'])

    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No scripts",
        'scripts': [],
        'count': 0 if type(u) is str or u == None else u.count() # type: ignore
    }
    if result['count'] > 0:
        result['status'] = True
        result['message'] = f"Found scripts: {result['count']}"
        result['scripts'] = data.collect(u)

    return result


def _create_script(data_pass: dict = {}) -> dict:
    result = scripts.insert(data_pass)
    return result


def _modify_script(data_pass: dict = {}) -> dict:
    result = scripts.modify(data_pass)
    return result


def _delete_script(data_pass: dict = {}) -> dict:
    result = scripts.delete(data_pass)
    return result


# Site modifiers and listings
def _sites(data_pass: dict = {}) -> dict:

    data_filter = utils.apply_filter(data_pass)
    u = sites.load(
        data_filter['filter'], data_filter['sort'], data_filter['exclude'])

    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No sites",
        'sites': [],
        'count': 0 if type(u) is str or u == None else u.count() # type: ignore
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


def _create_site(data_pass: dict = {}) -> dict:
    result = sites.insert(data_pass)
    return result


def _modify_site(data_pass: dict = {}) -> dict:
    result = sites.modify(data_pass)
    return result


def _delete_site(data_pass: dict = {}) -> dict:
    result = sites.delete(data_pass)
    return result


# Item modifiers and listings
def _items(data_pass: dict = {}) -> dict:

    data_filter = utils.apply_filter(data_pass)
    u = items.load(
        data_filter['filter'], data_filter['sort'], data_filter['exclude'])

    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No items",
        'items': [],
        'count': 0 if type(u) is str or u == None else len(u)
    }
    if result['count'] > 0:
        result['status'] = True
        result['message'] = f"Found items: {result['count']}"
        result['items'] = data.collect(u)

    return result


def _create_item(data_pass: dict = {}) -> dict:
    result = items.insert(data_pass)
    return result


def _modify_item(data_pass: dict = {}) -> dict:
    result = items.modify(data_pass)
    return result


def _delete_item(data_pass: dict = {}) -> dict:
    result = items.delete(data_pass)
    return result


# Search
def _search(data_pass: dict) -> dict:
    if type(data_pass) is dict and 'search' in data_pass:
        r = utils.index_eval()

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

        return {
            'search_term': data_pass['search'],
            'servers': data.collect(server_collection),
            'scripts': data.collect(script_collection),
            'users': data.collect(user_collection),
            'sites': data.collect(site_collection)
        }

    return {}


# Notifications
def _notifications(data_pass: dict = {}) -> dict:

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