from archon import app 
from archon.config import load_config
from archon.mailer import mailer
from archon.system import device


def _test(data_pass: dict = {}) -> dict:
    return {
        'test': "Ok",
        'mode': app.mode,
        'data_pass': data_pass
    }


def _get_enums(data_pass: dict = {}) -> dict:
    return app.config['enum_options']


def _is_email(data_pass: dict = {}) -> dict:
    return mailer.check_email(data_pass)


def _countries(data_pass: dict = {}) -> list:
    return load_config('iso-3166-1')
