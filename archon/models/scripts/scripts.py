import json
from bson.objectid import ObjectId
from archon import app, data, utils
from archon.models.notifications import notifications


def load(filter_data: dict | None = None, sort_data: list | None = None, exclude_data: dict | None = None):
    finder = {
        'collection': 'scripts',
        'filter': filter_data,
        'sort': sort_data,
        'exclude': exclude_data
    }
    return data.ex(finder)


def load_one(filter_data: dict):
    finder = {
        'collection': 'scripts',
        'filter': filter_data
    }
    return data.one(finder)


def modify(script_data: dict):
    result = validator(script_data)

    if 'id' not in script_data.keys():
        result['message'] = 'Need id to modify script'
        result['status'] = False

    if len(str(script_data['id'])) != 24:
        result['message'] = 'script id is invalid'
        result['status'] = False

    if result['status'] == True:

        finder = load_one({
            '$and': [
                {
                    '$or': [
                        {'name': script_data['name']},
                        {'content': script_data['content']}
                    ],
                },
                {
                    '_id': {
                        '$ne': ObjectId(script_data['id'])
                    }
                }
            ]
        })

        modify_script = load_one({
            '_id': ObjectId(script_data['id'])
        })

        if type(finder) is not dict and type(modify_script) is dict:
            _id = script_data.pop('id', None)
            script_data.pop('creator', None)
            script_data.pop('created_at', None)

            script = dict()
            script.update(modify_script)
            script.update(script_data)

            script['updater'] = app.store['user']['data']['id']
            script['updated_at'] = utils.now()

            changed = utils.detect_object_changes([
                'name',
                'description',
                'safe',
                'content'
            ], modify_script, script)

            scripts = app.db['scripts']

            if 'target' not in script or type(script['target']) != str:
                script['target'] = 'site'

            script = _model(script)
            scripts.update_one({'_id': ObjectId(_id)}, {'$set': script})

            result['message'] = f"script {script['name']} not modified"

            if changed == True:
                # Notification comes here
                result['message'] = f"script {script['name']} modified"
                notifications.db(
                    'script', str(_id), f"script {script['name']} was modified.", json.dumps(data.collect_one(script), indent=4))

            result['status'] = True
            result['changed'] = changed

        else:
            param_found = ''
            if finder['name'] == script_data['name']:
                param_found = f"with name {script_data['name']}"
            if len(param_found) == 0 and finder['content'] == script_data['content']:
                param_found = f"with same content"

            result['status'] = False
            result['message'] = f"script {param_found} already exists"

    return result


def insert(script_data: dict):
    result = validator(script_data)

    if result['status'] == True:

        script = _model(script_data)

        finder = load_one({
            '$or': [
                {'name': script['name']},
                {'content': script['content']}
            ]
        })

        if type(finder) is not dict:

            script_data.pop('id', None)
            script_data.pop('updated_at', None)

            script['created_at'] = utils.now()
            script['creator'] = app.store['user']['data']['id']

            if 'target' not in script or type(script['target']) != str:
                script['target'] = 'site'

            scripts = app.db['scripts']
            _id = scripts.insert_one(script)

            # Notification comes here
            html_message_data = {
                'app_full_name': app.config['full_name'],
                'app_name': app.config['name'],
                'username': app.store['user']['username'],
                'message': f"script {script['name']} was created."
            }
            notifications.email('settings.notifications.scripts',
                                'common-notification', f"{app.config['name']} - script created", html_message_data)
            notifications.db(
                'site', str(_id.inserted_id), f"script {script['name']} was created.", json.dumps(data.collect_one(script), indent=4))

            result['status'] = True
            result['message'] = f"script {script['name']} created"
        else:

            param_found = ''
            if finder['name'] == script['name']:
                param_found = f"with name {script['name']}"
            if len(param_found) == 0 and finder['content'] == script['content']:
                param_found = f"with same content"

            result['status'] = False
            result['message'] = f"script {param_found} already exists"

    return result


def delete(script_data: dict):
    result = {
        'status': False,
        'message': 'Need id to delete script',
        'script_data': script_data
    }

    if 'id' in script_data.keys():
        scripts = app.db['scripts']
        r = scripts.delete_one({'_id': ObjectId(script_data['id'])})
        result['delete_status'] = r.deleted_count
        result['status'] = False if r.deleted_count == 0 else True
        result['message'] = 'script delete error' if r.deleted_count == 0 else 'script deleted'

    return result


def validator(script_data: dict):
    result = {
        'status': False,
        'message': "Data error",
    }

    if 'content' in script_data.keys() and 'name' in script_data.keys():
        if type(script_data['name']) != str or len(script_data['name']) < 2:
            result['message'] = f"'{script_data['name']}' is not a valid script name"
            return result

        if type(script_data['content']) != str or len(script_data['content']) < 10:
            result['message'] = f"{script_data['name']} invalid script content"
            return result

        result['status'] = True

    return result


def _model(script_data: dict):

    script = {
        'name': utils.eval_key('name', script_data),
        'description': utils.eval_key('description', script_data),
        'safe': utils.eval_key('safe', script_data, 'bool'),
        'target': utils.eval_key('target', script_data),
        'content': utils.eval_key('content', script_data),
        'meta': utils.eval_key('meta', script_data, 'dict'),
        'settings': utils.eval_key('settings', script_data, 'dict'),
        'creator': utils.eval_key('creator', script_data),
        'updater': utils.eval_key('updater', script_data),
        'created_at': utils.eval_key('created_at', script_data),
        'updated_at': utils.eval_key('updated_at', script_data),
    }

    return script
