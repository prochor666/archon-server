from archon import app, utils
from archon.config import load_config
from archon.mailer import mailer

def _test(data_pass: dict = {}) -> dict:
    return {
        'status': True,
        'test': 'Ok',
        'mode': app.mode,
    }


def _get_enums(data_pass: dict = {}) -> dict:
    return app.config['enum_options']


def _is_email(email: str = '') -> dict:
    return mailer.check_email(email)


def _is_ip(ip: str) -> dict:
    return utils.ip_valid(ip)


def _countries(data_pass: dict = {}) -> list:
    return load_config('iso-3166-1')
