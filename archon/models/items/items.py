import json
from bson.objectid import ObjectId
from archon import app, data, utils
from archon.models.notifications import notifications


def load(filter_data: dict | None = None, sort_data: dict | None = None, exclude_data: dict | None = None):
    finder = {
        'collection': 'items',
        'filter': filter_data,
        'sort': sort_data,
        'exclude': exclude_data
    }
    return data.ex(finder)


def load_one(filter_data: dict):
    finder = {
        'collection': 'items',
        'filter': filter_data
    }
    return data.one(finder)


def modify(item_data: dict):
    result = validator(item_data)

    if 'id' not in item_data.keys():
        result['message'] = 'Need id to modify item'
        result['status'] = False

    if len(str(item_data['id'])) != 24:
        result['message'] = 'Item id is invalid'
        result['status'] = False

    if result['status'] == True:

        finder = load_one({
            '$and': [
                {
                    '$or': [
                        {'name': item_data['name']},
                        {'content': item_data['content']}
                    ],
                },
                {
                    '_id': {
                        '$ne': ObjectId(item_data['id'])
                    }
                }
            ]
        })

        modify_item = load_one({
            '_id': ObjectId(item_data['id'])
        })

        if type(finder) is not dict and type(modify_item) is dict:
            _id = item_data.pop('id', None)
            item_data.pop('creator', None)
            item_data.pop('created_at', None)

            item = dict()
            item.update(modify_item)
            item.update(item_data)

            item['updater'] = app.config['user']['_id']
            item['updated_at'] = utils.now()

            changed = utils.detect_object_changes([
                'name',
                'description',
                'safe',
                'content'
            ], modify_item, item)

            items = app.db['items']

            if 'target' not in item or type(item['target']) != str:
                item['target'] = 'site'

            item = _model(item)
            items.update_one({'_id': ObjectId(_id)}, {'$set': item})

            result['message'] = f"Item {item['name']} not modified"

            if changed == True:
                # Notification comes here
                result['message'] = f"Item {item['name']} modified"
                notifications.db(
                    'item', str(_id), f"Item {item['name']} was modified.", json.dumps(data.collect_one(item), indent=4))

            result['status'] = True
            result['changed'] = changed

        else:
            param_found = ''
            if finder['name'] == item_data['name']:
                param_found = f"with name {item_data['name']}"
            if len(param_found) == 0 and finder['content'] == item_data['content']:
                param_found = f"with same content"

            result['status'] = False
            result['message'] = f"item {param_found} already exists"

    return result


def insert(item_data: dict):
    result = validator(item_data)

    if result['status'] == True:

        item = _model(item_data)

        finder = load_one({
            '$or': [
                {'name': item['name']},
                {'content': item['content']}
            ]
        })

        if type(finder) is not dict:

            item_data.pop('id', None)
            item_data.pop('updated_at', None)

            item['created_at'] = utils.now()
            item['creator'] = app.config['user']['_id']

            if 'target' not in item or type(item['target']) != str:
                item['target'] = 'site'

            items = app.db['items']
            _id = items.insert_one(item)

            # Notification comes here
            html_message_data = {
                'app_full_name': app.config['name'],
                'username': app.config['user']['username'],
                'message': f"Item {item['name']} was created."
            }
            notifications.email('settings.notifications.items',
                                'common-notification', f"{app.config['name']} - item created", html_message_data)
            notifications.db(
                'site', str(_id.inserted_id), f"item {item['name']} was created.", json.dumps(data.collect_one(item), indent=4))

            result['status'] = True
            result['message'] = f"Item {item['name']} created"
        else:

            param_found = ''
            if finder['name'] == item['name']:
                param_found = f"with name {item['name']}"
            if len(param_found) == 0 and finder['content'] == item['content']:
                param_found = f"with same content"

            result['status'] = False
            result['message'] = f"Item {param_found} already exists"

    return result


def delete(item_data: dict):
    result = {
        'status': False,
        'message': 'Need id to delete item',
        'item_data': item_data
    }

    if 'id' in item_data.keys():
        items = app.db['items']
        r = items.delete_one({'_id': ObjectId(item_data['id'])})
        result['delete_status'] = r.deleted_count
        result['status'] = False if r.deleted_count == 0 else True
        result['message'] = 'Item delete error' if r.deleted_count == 0 else 'item deleted'

    return result


def validator(item_data: dict):
    result = {
        'status': False,
        'message': "Data error",
    }

    if 'content' in item_data.keys() and 'name' in item_data.keys():
        if type(item_data['name']) != str or len(item_data['name']) < 1:
            result['message'] = f"'{item_data['name']}' is not a valid item name"
            return result

        if type(item_data['content']) != str or len(item_data['content']) < 1:
            result['message'] = f"{item_data['name']} invalid item content"
            return result

        result['status'] = True

    return result


def _model(item_data: dict):

    item = {
        'name': utils.eval_key('name', item_data),
        'description': utils.eval_key('description', item_data),
        'content': utils.eval_key('content', item_data),
        'ref': utils.eval_key('ref', item_data, 'dict'),
        'meta': utils.eval_key('meta', item_data, 'dict'),
        'settings': utils.eval_key('settings', item_data, 'dict'),
        'creator': utils.eval_key('creator', item_data),
        'updater': utils.eval_key('updater', item_data),
        'created_at': utils.eval_key('created_at', item_data),
        'updated_at': utils.eval_key('updated_at', item_data),
    }

    return item
