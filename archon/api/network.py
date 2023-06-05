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


def _domain_info(domain: str, dns_records: str = None) -> dict: 
    result = {
        'status': False, 
        'message': 'Data error', 
        'data': None, 
        'domain': domain,
        'dns_records': dns_records
    }
    record_filter = []

    if type(dns_records) is list and len(dns_records) > 0: 
        record_filter = dns_records

    if type(dns_records) is str and len(dns_records) > 0:
        record_filter = dns_records.split(',')

    result['data'] = utils.domain_dns_info(
        str(domain), record_filter)
    if len(result['data']) > 0:
        result['message'] = f"Domain {domain} DNS records found"
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


def _scan_all_interfaces(data_pass: dict = {}) -> dict:
    scn = network.scan_all_interfaces()
    result = {
        'status': True,
        'message': 'Scanned',
        'data': scn
    }
    return result

def _scan_ip(ip: str, ports: str = None) -> dict:

    result = {
        'status': False,
        'message': 'Data error',
        'ip': ip,
        'ports': ports
    }

    if type(ports) is str:
        scan = network.scan_ip(ip, ports.split(','))
    elif type(ports) is list:
        scan = network.scan_ip(ip, ports)
    else:
        scan = network.scan_ip(ip)

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


