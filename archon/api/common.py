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


def _is_email(email: str = '') -> dict:
    return mailer.check_email(email)


def _is_ip(ip: str) -> dict:
    return utils.ip_valid(ip)


def _countries(data_pass: dict = {}) -> list:
    return load_config('iso-3166-1')


def _help():
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