import json
from archon import app, data, utils
from archon.network import monitoring, remote
from archon.models.servers import servers


def _test_connection(data_pass: dict = {}) -> dict:
    result = {
        'status': False,
        'message': 'Data error',
        'data': data_pass,
        'shell': []
    }

    if 'server_id' in data_pass.keys() and len(data_pass['server_id']) > 0:
        result = remote.test_connection(data_pass['server_id'])

    return result


def _deploy(data_pass: dict = {}) -> dict:
    result = {
        'status': False,
        'message': 'Data error',
        'data': []
    }

    if 'id' in data_pass.keys() and type(data_pass['id']) is str and len(data_pass['id']) > 0:
        result = remote.deploy(data_pass['id'])

    return result


def _detect_root(data_pass: dict = {}) -> dict:
    result = {
        'status': False,
        'message': 'Data error',
        'data': []
    }

    if 'id' in data_pass.keys() and type(data_pass['id']) is str and len(data_pass['id']) > 0:
        result = remote.detect_root(data_pass['id'])

    return result


# Monitoring
def _install_monitoring_service(data_pass: dict = {}) -> dict:
    result = {
        'status': False,
        'message': 'Data error',
        'shell': []
    }

    if 'id' in data_pass.keys() and len(data_pass['id']) > 0:
        result = remote.install_monitoring_service(data_pass['id'])

    return result


def _monitor_server(data_pass: dict = {}) -> dict:
    if type(data_pass) is dict and 'id' in data_pass:

        mntd = monitoring.survey(data_pass['id'])
        if 'data' in mntd.keys() and 'cpu' in mntd['data'].keys() and 'last_update' in mntd['data'].keys() and len(mntd['data']['cpu']) > 0 and len(mntd['data']['last_update']) > 0:
            return mntd

    return {
        'status': False,
        'message': f"Server id is missing",
        'data': []
    }


def _monitoring(data_pass: dict = {}) -> dict:
    cache_file = f"{app.config['filesystem']['resources']}/monitoring.json"

    try:
        with open(cache_file) as dump:
            result = json.load(dump)
            result['resource'] = 'cache'
    except Exception as error:
        result = _monitor_servers()
        result['resource'] = 'direct'

    return result


def _monitor_servers(data_pass: dict = {}) -> dict:
    result = {
        'status': False,
        'message': f"Monitoring results",
        'data': []
    }
    u = servers.load({
            'publish': True,
            'use': True
    })
    count = 0 if type(u) is str or u == None else u.count() # type: ignore

    if count > 0:
        server_collection = data.collect(u)

        for server in server_collection:
            mntd = monitoring.survey(server['_id'])
            if 'data' in mntd.keys() and 'cpu' in mntd['data'].keys() and 'last_update' in mntd['data'].keys() and len(mntd['data']['cpu']) > 0 and len(mntd['data']['last_update']) > 0:
                result['data'].append(mntd)

        result['status'] = True

        # Cache data file localy
        utils.file_save(f"{app.config['filesystem']['resources']}/monitoring.json",
                        json.dumps(result))

    return result