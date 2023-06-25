import yaml
from archon import app, compat, utils
from archon.api import assets, users 

compat.check_version()
app.mode = 'cli'

app.store['user'] = users._get_system_user()

def get_section(section, data):
    return data[section] if section in data and type(data[section]) is list else []


def randomize_strings(drop):
    for key in drop.keys():
        if type(drop[key]) is str:
            drop[key] = drop[key].replace('_%randomstr%', utils.rnd(10)) 
            
    return drop


def devdrop(section, section_data):
    drops = []
    
    for drop in section_data:
        match section:
            case 'users':
                drop_result = users._user_create(randomize_strings(drop))
                drops.append({
                    'result': drop_result,
                    'data': drop,
                })
            case 'items':
                drop_result = assets._item_create(randomize_strings(drop))
                drops.append({
                    'result': drop_result,
                    'data': drop,
                })
            case _:
                pass
    return drops


def cli_app():

    sections = ['users', 'items', 'servers', 'scripts', 'sites']
    data = {}
    result = {}

    devdrop_file = app.config['devdrop']['file']
    with open(devdrop_file) as config:
        data = yaml.load(config, Loader=yaml.Loader)

        for section in sections: 
            section_data = get_section(section=section, data=data)
            result[section] = devdrop(section=section, section_data=section_data)

    return result

if __name__ == "__main__":
    print(yaml.dump(cli_app()))
    