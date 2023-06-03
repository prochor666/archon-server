import json
from archon import app 
from archon.mailer import mailer
from archon.system import device


def _about(data_pass: dict = {}) -> dict:
    data = {
        'OS': device.sys_info(),
        'Network': device.network_info(),
        'CPU': device.cpu_info(),
        'Memory': device.memory_info(),
        'Disk': device.disk_info()
    }
    return data


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
    try:
        with open('json/iso-3166-1.json') as countries:
            return json.load(countries)
    except Exception as error:
        return []

