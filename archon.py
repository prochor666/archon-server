import argparse, json, yaml
from archon import app, compat, utils, colors
from archon.api import assets, auth, common, db, network, remote, system,  users 
from archon.auth import auth as authorization

#compat.check_version()
app.mode = 'cli'

parser = argparse.ArgumentParser(
    description="Archon command line tool",
    epilog="All accessible arguments listed above"
)


def insert(msg, indent = True):
    print()
    print(msg)


def create_endpoint_argset(endpoint):
    argset = {
        "decorator": "",
        "required": [],
        "optional": []
    }
    conf = app.config['api']['cli'][endpoint]
    keys = conf.keys()
    
    if 'decorator' in keys:
        argset['decorator'] = conf['decorator']
    
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
    
    pass


parser.add_argument('endpoint', help="Specify API method")

args, unknown = parser.parse_known_args()
data_pass = utils.validate_data_pass(dict(vars(args)))
endpoint = data_pass.pop('endpoint', None)

if endpoint != None and endpoint in app.config['api']['cli']:

    endpoint_schema = create_endpoint_argset(endpoint)

    for required_arg in endpoint_schema['required']:
        parser.add_argument(f"-{required_arg}", type=str)

    for optional_arg in endpoint_schema['optional']:
        parser.add_argument(f"-{optional_arg}", type=str, nargs='+')

    args, unknown = parser.parse_known_args()
    data_pass = utils.validate_data_pass(dict(vars(args)))

    app.store['user'] = users._get_system_user()

    if type(app.store['user']) is dict:
        parsed_decorator = app.config['api']['cli'][endpoint]['decorator'].split('.')
        module = parsed_decorator[0]
        method = parsed_decorator[1]
        
        obj = globals()
        result = getattr(obj[module], method)(data_pass)
        
        who = f" [Archon-{app.config['version']}]@{app.store['user']['username']} "
        
        insert(f"👽 {colors.mod(who, 'lightcyan_ex', 'blue')}")
        
        if type(result) == dict:
            status = True
            message = f"task '{endpoint}' completed successfully"

            if 'status' in result:
                status = result['status']
                result.pop('status', None)

            if 'message' in result:
                message = result['message']
                result.pop('message', None)

            insert(utils.format_response(status, message))
            
            insert(f"⚙ {colors.mod('  Data [Dict]  ', 'yellow', 'blue')}")
            
            result_json = json.dumps(dict(result), indent=4)
            insert(result_json)
            
            """
            for key, value in result.items():
                print(f"  {colors.fg(key, 'lightcyan_ex')}: {str(value)}")
            """
        if type(result) == list or type(result) == tuple or type(result) == set:

            insert(f"⚙ {colors.mod('  Data  [List]  ', 'yellow', 'blue')}")
            
            for i in range(result):
                print(str(result[i]), True if i == 0 else False)

        print()

else:
    insert(utils.format_response(False, f"endpoint '{endpoint}' 👻 is not allowed"))
    print()
"""     
    
if __name__ == "__main__":
    cmd() """