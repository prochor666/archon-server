from archon import data, utils
from archon import app
from archon.mailer import mailer


def load(filter_data: dict | None = None, sort_data: dict | None = None, exclude_data: dict | None = None) -> list:
    finder = {
        'collection': 'notifications',
        'filter': filter_data,
        'sort': sort_data,
        'exclude': exclude_data
    }
    return data.ex(finder)


def email(case: str, template: str, subject: str, html_message_data: dict, att: str = ''):
    if app.config['user']['username'] != 'system':
        valid_users = data.collect(data.ex({
            'collection': 'users',
            'filter': {
                case: True
            }
        })) # type: ignore

        for user in valid_users:
            html_message_data['user'] = user
            html_message = mailer.assign_template(
                template, html_message_data)
            mailer.send(
                user['email'], subject, html_message, att)


def db(obj_type: str, obj_id: str, message: str, json_data: str):
    notifs = app.db['notifications']
    notification = {
        'user_id': app.config['user']['_id'],
        'created_at': utils.now(),
        'obj_type': obj_type,
        'obj_id': obj_id,
        'message': message,
        'json_data': json_data
    }
    notifs.insert_one(notification)
