import json
from archon import app, data, utils
from archon.models.devices import devices

# Item modifiers and listings
def _devices(data_pass: dict = {}) -> dict:
    _filter = utils.ark(data_pass, 'filter')
    _sort = utils.ark(data_pass, 'sort')

    if type(_filter) is str:
        data_pass['filter'] =  json.loads(_filter) if len(_filter) > 0 else {}

    if type(_sort) is str:
        data_pass['sort'] = json.loads(_sort) if len(_sort) > 0 else {}

    data_filter = utils.apply_filter(data_pass)
    u = devices.load(
        data_filter['filter'], data_filter['sort'], data_filter['exclude'])

    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No devices",
        'count': 0 if type(u) is not list or u == None else len(u),
        'devices': [],
    }
    if result['count'] > 0:
        result['status'] = True
        result['message'] = f"Found devices: {result['count']}"
        result['devices'] = data.collect(u)

    return result


def _device_one(id: str) -> dict:
    r = devices.load_one(filter_data = {
        'id': id
    })

    result = {
        'status': False,
        'message': "No device",
        'device': {},
    }

    if type(r).__name__ == 'dict':
        #r['_id'] = str(r['_id'])
        result['status'] = True
        result['device'] = data.collect_one(r)
        result['message'] = f"Found device"
    return result


def _device_pair(mac: str) -> dict:
    r = devices.load_one(filter_data = {
        'mac': mac
    })

    result = {
        'status': False,
        'message': "No device",
        'mac': mac,
        'pin': utils.rnd(6, digits_only = True),
        'device': {},
    }

    if type(r).__name__ == 'dict':
        #r['_id'] = str(r['_id'])
        result['status'] = True
        result['device'] = data.collect_one(r)
        result['message'] = f"Found device"
    return result


def _device_create(data_pass: dict = {}) -> dict:
    result = devices.insert(data_pass)
    return result


def _device_modify(data_pass: dict = {}) -> dict:
    result = devices.modify(data_pass)
    return result


def _device_delete(data_pass: dict = {}) -> dict:
    result = devices.delete(data_pass)
    return result