import argparse, json, yaml
from archon import app, compat, utils, colors
from archon.api import assets, auth, common, db, network, remote, system,  users 
from archon.auth import auth as authorization


compat.check_version()
app.mode = 'cli'


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

    if endpoint != None and endpoint in app.config['api']['cli']:

        endpoint_schema = create_endpoint_argset(endpoint)

        for required_arg in endpoint_schema['required']:
            parser.add_argument(f"-{required_arg}", type=str)

        for optional_arg in endpoint_schema['optional']:
            parser.add_argument(f"-{optional_arg}", type=str, nargs='+')

        #args, unknown = parser.parse_known_args()
        data_pass = utils.validate_data_pass(vars(parser.parse_args()))

        app.store['user'] = users._get_system_user()

        if type(app.store['user']) is dict:
            parsed_api_method = app.config['api']['cli'][endpoint]['api_method'].split('.')
            module = parsed_api_method[0]
            method = parsed_api_method[1]

            obj = globals()
            result = getattr(obj[module], method)(data_pass)

            who = f" [Archon-{app.config['version']}]@{app.store['user']['username']} "
            intro = f"👽 {colors.mod(who, 'lightcyan_ex', 'blue')}"
            data_mode = f" Result ok: {type(result).__name__}  "
            data_status_and_mode = f"🧪 {colors.mod(data_mode, 'white', 'green')}"

            if type(result) == dict:
                status = True
                message = f"task '{endpoint}' completed successfully"

                if 'status' in result:
                    status = result['status']
                    result.pop('status', None)

                if 'message' in result:
                    message = result['message']
                    result.pop('message', None)

                if status == False:
                    data_mode = f" Result fail: {type(result).__name__}  "
                    data_status_and_mode = f"🧪 {colors.mod(data_mode, 'white', 'red')}"

                method_response = utils.format_response(status, message)
                result_json = json.dumps(result, indent=4)

                output_buffer.append(intro)
                output_buffer.append(data_status_and_mode)
                output_buffer.append(method_response)
                output_buffer.append(result_json)

            if type(result) == list or type(result) == tuple or type(result) == set:
                result_json = json.dumps(result, indent=4)
                
                output_buffer.append(intro)
                output_buffer.append(data_status_and_mode)
                output_buffer.append('')
                output_buffer.append(result_json)

            output_buffer.append(' ')

    else:
        output_buffer.append(
            utils.format_response(False, f"endpoint '{endpoint}' 👻 is not allowed"))
        output_buffer.append(' ')


    print('\n'.join(output_buffer))
    


if __name__ == "__main__":
    cli_app()
