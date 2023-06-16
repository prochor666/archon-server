import argparse, json, yaml
from archon import app, compat, utils, colors
from archon.api import assets, auth, common, db, network, remote, system, users 
from archon.auth import auth as authorization
import os

compat.check_version()
app.mode = 'cli'


def callback_with_vars(endpoint_schema: dict, data_pass: dict) -> dict:
    result = {}
    for required_arg in endpoint_schema['required']:
        if required_arg in data_pass:
            result[required_arg] = data_pass[required_arg]

    for optional_arg in endpoint_schema['optional']:
        if optional_arg in data_pass:
            result[optional_arg] = data_pass[optional_arg]

    return result

def create_endpoint_argset(endpoint: str) -> dict:
    argset = {
        "api_method": "",
        "required": [],
        "optional": []
    }
    conf = app.config['api']['cli'][endpoint]
    keys = conf.keys()

    if 'api_method' in keys:
        argset['api_method'] = conf['api_method']

    if 'valid_schema' in keys and \
        'v1' in conf['valid_schema'].keys() and \
        'arguments' in conf['valid_schema']['v1'].keys():

        args = conf['valid_schema']['v1']['arguments']
        for key in args.keys():

            if args[key] == True:
                argset['required'].append(key)
            else: 
                argset['optional'].append(key)

    return argset


def cli_app():

    parser = argparse.ArgumentParser(
        description="Archon command line tool",
        epilog="All accessible arguments listed above"
    )

    parser.add_argument('endpoint', help="Specify API method")
    output_buffer = []

    args, unknown = parser.parse_known_args()
    data_pass = utils.validate_data_pass(vars(args))
    endpoint = data_pass.pop('endpoint', None)

    function_args = {}

    if endpoint != None and endpoint in app.config['api']['cli']:

        endpoint_schema = create_endpoint_argset(endpoint)

        for required_arg in endpoint_schema['required']:
            parser.add_argument(f"-{required_arg}", type=str)

        for optional_arg in endpoint_schema['optional']:
            parser.add_argument(f"-{optional_arg}", type=str)

        args, unknown = parser.parse_known_args()
        # data_pass = utils.validate_data_pass(vars(args))
        data_pass = utils.validate_data_pass(vars(parser.parse_args()))

        app.store['user'] = users._get_system_user()

        display_username = f"[{os.getlogin()} /as {app.store['user']['username']}]"
        if type(display_username) is not str:
            display_username = app.store['user']['username']
        # Consider or not to use
        # import getpass
        #display_username = getpass.getuser()

        if type(app.store['user']) is dict:
            function_args = callback_with_vars(endpoint_schema, data_pass)
            parsed_api_method = app.config['api']['cli'][endpoint]['api_method'].split('.')
            module = parsed_api_method[0]
            method = parsed_api_method[1]
            who = f" 👽 {display_username}@Archon-{app.config['version']} "
            intro = f"{colors.mod(who, 'lightcyan_ex', 'blue')}"

            try: 
                obj = globals()
                result = getattr(obj[module], method)(**function_args)
                data_mode = f"{endpoint} result is: {type(result).__name__}  "
                data_status_and_mode = f"{colors.mod(' 🧪 ' + data_mode, 'white', 'magenta')}"
                status = True
                message = f"task '{endpoint}' completed"

                if status == False:
                    data_status_and_mode = f"{colors.mod(' 🧪 ' + data_mode, 'white', 'red')}"

                method_response = utils.format_response(status, message)

                if type(result) == dict or \
                    type(result) == list or \
                    type(result) == tuple or \
                    type(result) == set:
                    result_output = json.dumps(result, indent=4)
                else: 
                    result_output = str(result)

                output_buffer.append('')
                output_buffer.append(intro + data_status_and_mode)
                output_buffer.append('')
                output_buffer.append(method_response)
                output_buffer.append(result_output)
                output_buffer.append('')

            except Exception as e:
                status = False
                data_mode = f"{endpoint} "
                data_status_and_mode = f"{colors.mod(' 🧪 ' + data_mode, 'white', 'magenta')}"
                method_response = utils.format_response(status, json.parse({'error': e}))

                output_buffer.append('')
                output_buffer.append(intro + data_status_and_mode)
                output_buffer.append('')
                output_buffer.append(method_response)
                output_buffer.append('') 

    else:
        output_buffer.append(
            utils.format_response(False, f"endpoint '{endpoint}' 👻 is not allowed"))
        output_buffer.append('')

    print('\n'.join(output_buffer))


if __name__ == "__main__":
    cli_app()
