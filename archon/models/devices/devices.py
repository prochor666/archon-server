import json
from bson.objectid import ObjectId
from archon import app, data, utils
from archon.models.notifications import notifications
from archon.models.users import users

def load(filter_data: dict | None = None, sort_data: list | None = None, exclude_data: dict | None = None):
    finder = {
        'collection': 'devices',
        'filter': filter_data,
        'sort': sort_data,
        'exclude': exclude_data
    }
    return data.ex(finder)


def load_one(filter_data: dict):
    finder = {
        'collection': 'devices',
        'filter': filter_data
    }
    return data.one(finder)


def modify(device_data: dict, audit_system: bool = False) -> dict:
    result = validator(device_data)

    if 'id' not in device_data.keys():
        result['message'] = 'Need id to modify device'
        result['status'] = False

    if len(str(device_data['id'])) != 24:
        result['message'] = 'Device id is invalid'
        result['status'] = False

    if result['status'] == True:

        finder = load_one({
            '$and': [
                {
                    '$and': [
                        {'mac': device_data['mac']},
                        {'ref': device_data['ref']}
                    ],
                },
                {
                    '_id': {
                        '$ne': ObjectId(device_data['id'])
                    }
                }
            ]
        })

        modify_device = load_one({
            '_id': ObjectId(device_data['id'])
        })

        if type(finder) is not dict and type(modify_device) is dict:
            _id = device_data.pop('id', None)
            device_data.pop('creator', None)
            device_data.pop('created_at', None)

            device = dict()
            device.update(modify_device)
            device.update(device_data)

            if audit_system == True:
                system_user = users.system_user()
                device['updater'] = system_user['_id']
            else:
                device['updater'] = app.store['user']['data']['id']
            device['updated_at'] = utils.now()

            changed = utils.detect_object_changes([
                'name',
                'description',
                'type',
                'content',
                'active',
                'ref',
                'meta',
                'settings',
            ], modify_device, device)

            devices = app.db['devices']

            if 'target' not in device or type(device['target']) != str:
                device['target'] = 'site'

            device = _model(device)
            devices.update_one({'_id': ObjectId(_id)}, {'$set': device})

            result['message'] = f"Device {device['name']} not modified"

            if changed == True:
                # Notification comes here
                result['message'] = f"Device {device['name']} modified"
                notifications.db(
                    'device', str(_id), f"Device {device['name']} was modified.", json.dumps(data.collect_one(device), indent=4), audit_system)

            result['status'] = True
            result['changed'] = changed

        else:
            param_found = ''
            if finder['name'] == device_data['name']:
                param_found = f"with name {device_data['name']}"
            if len(param_found) == 0 and finder['ref'] == device_data['ref']:
                param_found = f"with same ref"

            result['status'] = False
            result['message'] = f"device {param_found} already exists"

    return result


def insert(device_data: dict, audit_system: bool = False):
    result = validator(device_data)

    if result['status'] == True:

        device = _model(device_data)

        finder = load_one({
            '$and': [
                {'mac': device['mac']},
                {'ref': device['ref']}
            ]
        })

        if type(finder) is not dict:

            device_data.pop('id', None)
            device_data.pop('updated_at', None)

            if audit_system == True:
                system_user = users.system_user()
                device['creator'] = system_user['_id']
                creator_username = system_user['username']
            else:
                device['creator'] = app.store['user']['data']['id']
                creator_username = app.store['user']['data']['username']
            device['created_at'] = utils.now()
            
            if 'target' not in device or type(device['target']) != str:
                device['target'] = 'site'

            devices = app.db['devices']
            _id = devices.insert_one(device)

            # Notification comes here
            html_message_data = {
                'app_full_name': app.config['full_name'],
                'app_name': app.config['name'],
                'username': creator_username,
                'message': f"Device {device['name']} was created."
            }
            notifications.email('settings.notifications.devices',
                                'common-notification', f"{app.config['name']} - device created", html_message_data)
            notifications.db(
                'site', str(_id.inserted_id), f"device {device['name']} was created.", json.dumps(data.collect_one(device), indent=4))

            result['status'] = True
            result['message'] = f"Device {device['name']} created"
        else:

            param_found = ''
            if finder['mac'] == device['mac']:
                param_found = f"with mac address {device['mac']}"
            if len(param_found) == 0 and finder['content'] == device['content']:
                param_found = f"with same content"

            result['status'] = False
            result['message'] = f"Device {param_found} already exists"

    return result


def delete(device_data: dict) -> dict:
    result = {
        'status': False,
        'message': 'Need id to delete device',
        'device_data': device_data
    }

    if 'id' in device_data.keys():
        devices = app.db['devices']
        r = devices.delete_one({'_id': ObjectId(device_data['id'])})
        result['delete_status'] = r.deleted_count
        result['status'] = False if r.deleted_count == 0 else True
        result['message'] = 'Device delete error' if r.deleted_count == 0 else 'device deleted'

    return result


def validator(device_data: dict) -> dict:
    result = {
        'status': False,
        'message': "Data error",
    }

    if 'mac'in device_data.keys() and 'name'in device_data.keys() and 'ip' in device_data.keys():

        if type(device_data['mac']) != str or len(device_data['mac']) < 1:
            result['message'] = 'MAC address is not defined'
            return result
        else:
            mac_valid = utils.mac_valid(device_data['mac']) 
            if mac_valid['status'] == False:
                result['message'] = f"'{device_data['mac']}' is not a valid MAC address"
                return result
            
        if type(device_data['ip']) != str or len(device_data['ip']) < 1:
            result['message'] = 'IP address is not defined'
            return result
        else:
            ip_valid = utils.ip_valid(device_data['ip']) 
            if ip_valid['status'] == False:
                result['message'] = f"'{device_data['ip']}' is not a valid IP address"
                return result
        
        if type(device_data['name']) != str or len(device_data['name']) < 1:
            result['message'] = f"'{device_data['name']}' is not a valid device name"
            return result

        result['status'] = True

    return result


def _model(device_data: dict) -> dict:

    device = {
        'name': utils.eval_key('name', device_data),
        'mac': utils.eval_key('mac', device_data),
        'ip': utils.eval_key('ip', device_data),
        'ip_type': utils.eval_key('ip_type', device_data),
        'description': utils.eval_key('description', device_data),
        'content': utils.eval_key('content', device_data),
        'type': utils.eval_key('type', device_data),
        'active': utils.eval_key('active', device_data, 'bool'),
        'ref': utils.eval_key('ref', device_data),
        'meta': utils.eval_key('meta', device_data, 'dict'),
        'settings': utils.eval_key('settings', device_data, 'dict'),
        'creator': utils.eval_key('creator', device_data),
        'updater': utils.eval_key('updater', device_data),
        'created_at': utils.eval_key('created_at', device_data),
        'updated_at': utils.eval_key('updated_at', device_data),
    }

    return device
