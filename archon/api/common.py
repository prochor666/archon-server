from archon import app, colors, utils
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


def _is_email(data_pass: dict = {}) -> dict:
    email = utils.ark('email', data_pass)
    return mailer.check_email(email)


def _is_ip(data_pass: dict = {}) -> dict:
    ip = utils.ark('ip', data_pass)
    return utils.ip_valid(ip)


def _countries() -> dict:
    result = {
        'status': False,
        'message': 'Failed',
        'data': {}
    }
    c = load_config('iso-3166-1')
    l = len(c)
    if type(c) is list and l > 0:
        result['data'] = c
        result['status'] = True
        result['message'] = f"Ok, found {str(l)} countries"
        
    return result


def _help(data_pass: dict = {}):
    result = f"""{colors.fg('Archon help', 'LIGHTGREEN_EX')}
{colors.fg('Linux/Mac', 'LIGHTGREEN_EX')}: ./arc command -argument <value>
{colors.fg('Windows', 'LIGHTGREEN_EX')}: arc.cmd command -argument <value>
---------------------------------------
Commands
{colors.fg('**', 'lightred_ex')}  required
{colors.fg('**', 'lightgreen_ex')}  optional
---------------------------------------
"""

    for endpoint in app.config['api']['cli'].keys():
        schema = app.config['api']['cli'][endpoint]['valid_schema']['v1']
        required = []
        optional = []
        
        if 'arguments' in schema:
            args = app.config['api']['cli'][endpoint]['valid_schema']['v1']['arguments']

            for key in args.keys():
                if args[key] == True:
                    required.append(f" -{colors.fg(key, 'lightred_ex')} <value>")
                else: 
                    optional.append(f" -{colors.fg(key, 'lightgreen_ex')} <value>")

        r = ''.join(required)
        o = ''.join(optional)
        line = f"""
    {colors.fg(endpoint, 'lightcyan_ex')}{r}{o}"""
        result = result + line

    return result