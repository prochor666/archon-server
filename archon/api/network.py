import re
from archon import app, utils
from archon.network import network

def _ssh_keys(data_pass: dict = {}) -> dict:

    result = {
        'status': True,
        'message': 'Keys list',
        'data': utils.list_ssh_keys()
    }

    return result


def _domain_info(data_pass: dict = {}) -> dict: 
    result = {
        'status': False, 
        'message': 'Data error', 
        'data': None, 
        'pass': data_pass
    }
    record_filter = []

    if 'filter' in data_pass.keys(): # type: ignore

        if type(data_pass['filter']) is list and len(data_pass['filter']) > 0: 
            record_filter = data_pass['filter']

        if type(data_pass['filter']) is str and len(data_pass['filter']) > 0:
            record_filter = data_pass['filter'].split(',')

    if 'domain' in data_pass.keys():
        result['data'] = utils.domain_dns_info(
            str(data_pass['domain']), record_filter)
        if len(result['data']) > 0:
            result['message'] = f"Domain {str(data_pass['domain'])} DNS records found"
            result['status'] = True

    return result


def _client_ip(data_pass: dict = {}) -> dict:
    return {
        'status': True,
        'message': 'Client ip address',
        'ip': app.store['client_ip']
    }


def _ip(data_pass: dict = {}) -> list:
    return network.device_ip()


def _scan(data_pass: dict = {}) -> dict:
    scn = network.scan()
    result = {
        'status': True,
        'message': 'Scanned',
        'data_pass': data_pass,
        'ips': scn
    }
    return result

def _scan_ip(data_pass: dict = {}) -> dict:

    result = {
        'status': False,
        'message': 'Data error',
        'data_pass': data_pass
    }

    if 'ip' in data_pass.keys():
        if 'ports' in data_pass.keys() and type(data_pass['ports']) is str:
            scan = network.scan_ip(data_pass['ip'], str(data_pass['ports']).split(',')) # type: ignore
        elif 'ports' in data_pass.keys() and type(data_pass['ports']) is list:
            scan = network.scan_ip(data_pass['ip'], data_pass['ports']) # type: ignore
        else:
            scan = network.scan_ip(data_pass['ip'])

        result['status'] = scan['scan_status']
        result['message'] = scan['scan_result']
        result['ports'] = scan['ports']
        result['time'] = scan['time']
        result['ttl'] = scan['ttl']
    return result


def _validate_domain(data_pass: dict = {}) -> dict:
    result = {
        'status': False,
        'message': 'Data error',
    }

    if 'domain' in data_pass.keys() and type(data_pass['domain']) is str and len(data_pass['domain']) > 0:
        pre = re.compile(
            r'^(?=.{1,253}$)(?!.*\.\..*)(?!\..*)([a-zA-Z0-9-]{,63}\.){,127}[a-zA-Z0-9-]{1,63}$')
        if not pre.match(data_pass['domain']):
            result['message'] = f"Domain name {data_pass['domain']} is invalid"
        else:
            result['status'] = True
            result['message'] = f"Domain name {data_pass['domain']} is valid"

    return result


