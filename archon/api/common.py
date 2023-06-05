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


def _help():
    result = [
        f"Usage: ./arc command -argument <value>",
        f"HINT: for Windows use ./arc.cmd command -argument <value>",
        "",
    ]
    for endpoint in app.config['api']['cli'].keys():
        schema = app.config['api']['cli'][endpoint]['valid_schema']['v1']
        required = []
        optional = []
        
        if 'arguments' in schema:
            args = app.config['api']['cli'][endpoint]['valid_schema']['v1']['arguments']

            for key in args.keys():
                if args[key] == True:
                    required.append(f"-{key} <value>")
                else: 
                    optional.append(f"-{key} <value>")
                
        r = ' '.join(required)
        o = ' '.join(optional)
        line = f"""{endpoint} {r} {o} """
        result.append(line)

    return result