import yaml
import os


def locate_dirs():
    return {'templates': 'templates', 'config': 'config', 'static': 'static', 'storage': 'storage'}


def app_config():
    app_dirs = locate_dirs()
    with open(app_dirs['config']+'/app.yaml') as config:
        data = yaml.load(config, Loader=yaml.Loader)
        data['app_dirs'] = app_dirs

        for key, value in data['filesystem'].items():
            data['filesystem'][key] = value.replace('/', os.path.sep)

        data['api'] = api_config()
        data['smtp'] = smtp_config()

        return data

    return {}


def configure():
    _config = app_config()
    _config['store'] = {}
    return _config


def api_config():
    app_dirs = locate_dirs()
    with open(app_dirs['config']+'/api.yaml') as api:
        data = yaml.load(api, Loader=yaml.Loader)
        return data['api']

    return {}


def load_config(custom_config):
    app_dirs = locate_dirs()
    with open(f"{app_dirs['config']}/{custom_config}.yaml") as conf:
        data = yaml.load(conf, Loader=yaml.Loader)
        return data
    
    return {}


def smtp_config():
    app_dirs = locate_dirs()
    with open(app_dirs['config']+'/smtp.yaml') as smtp:
        data = yaml.load(smtp, Loader=yaml.Loader)
        return data

    return {}
