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

    # print(json.dumps(app.store, indent = 4))
    
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


def _device_pair(data_pass: dict) -> dict:
    r = devices.load_one(filter_data = {
        'mac':  utils.ark(data_pass, 'mac')
    })

    result = {
        'status': False,
        'message': "No device",
        'mac': utils.ark(data_pass, 'mac'),
        'pin': utils.rnd(6, digits_only = True),
        'device': data_pass,
    }

    # print(json.dumps(app.store, indent = 4))

    if type(r).__name__ == 'dict':
        #r['_id'] = str(r['_id'])
        device_data_found = data.collect_one(r)
        data_pass['id'] = device_data_found['_id']
        data_pass['ip'] = app.store['client_ip']
        device_data_found.update(data_pass)
        device_data_found['meta']['last_update'] = utils.now()
        mod = devices.modify(device_data = device_data_found, audit_system = True)
        #print(json.dumps(device_data_found, indent = 4))
        result['status'] = mod['status']
        result['device'] = data_pass
        result['message'] = f"Found device"
    else:
        data_pass['ip'] = app.store['client_ip']
        data_pass['name'] = f"{data_pass['mac']}-{app.store['client_ip']}"
        data_pass['meta']['last_update'] = utils.now()
        data_pass['settings'] = {
            'pin': utils.rnd(6, digits_only = True),
            'master': False,
            'contentPath': 'default'
        }
        mod = devices.insert(device_data = data_pass, audit_system = True)
        result['status'] = mod['status']
        result['device'] = data_pass
        result['message'] = f"Found device"
        
    #print(json.dumps(result, indent = 4))
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