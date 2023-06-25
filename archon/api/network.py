import re
from archon import app, utils
from archon.network import network


def ttl_from_str(ttl: str) -> float:
    if type(ttl) is str:
        ttl = ttl.replace(',', '.')
        try:
            ttl = float(ttl)
        except ValueError:
            pass
    else: 
        if 'scan_ip' in app.config and 'ttl' in app.config['scan_ip'] and type(app.config['scan_ip']["ttl"]) in [float, int]:
            ttl = app.config['scan_ip']["ttl"]

    return ttl


def _ssh_keys(data_pass: dict = {}) -> dict:

    result = {
        'status': True,
        'message': 'Keys list',
        'data': utils.list_ssh_keys()
    }

    return result


def _domain_info(data_pass: dict = {}) -> dict: 
    domain = utils.ark('domain', data_pass)
    dns_records = utils.ark('dns_records', data_pass, '')
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
    return {
        'status': True,
        'message': 'Client ip address list',
        'data': network.device_ip()
    }


def _scan_all_interfaces(data_pass: dict = {}) -> dict:
    ttl = ttl_from_str(utils.ark('ttl', data_pass, None))
    ports = utils.ark('ports', data_pass, '80, 443, 3306')
    
    result = {
        'status': False,
        'message': 'Data error',
        'data': []
    }

    if type(ttl) is not float:
        result['message'] = 'ttl must be float'
        return result

    if type(ports) is str:
        scan = network.scan_all_interfaces(ports.split(','), ttl)
    else:
        scan = network.scan_all_interfaces(ports, ttl)

    if type(scan) is list and len(scan) > 0:
        result['status'] = True
        result['message'] = 'Scanned'
    else:
        result['message'] = 'No interfaces found'
    
    result['data'] = scan
    
    return result

def _scan_ip(data_pass: dict = {}) -> dict:
    ttl = ttl_from_str(utils.ark('ttl', data_pass, None))
    ports = utils.ark('ports', data_pass, '80, 443, 3306')
    ip = utils.ark('ip', data_pass)

    result = {
        'status': False,
        'message': 'Data error',
        'ip': ip,
        'ports': ports
    }

    if type(ttl) is not float:
        result['message'] = 'ttl must be float'
        return result

    if type(ports) is str:
        scan = network.scan_ip(ip, ports.split(','), ttl)
    else:
        scan = network.scan_ip(ip, ports, ttl)
    
    result['status'] = scan['scan_status']
    result['message'] = scan['scan_result']
    result['ports'] = scan['ports']
    result['time'] = scan['time']
    result['ttl'] = scan['ttl']
    return result


def _validate_domain(data_pass: dict = {}) -> dict:
    domain = utils.ark('domain', data_pass)
    result = {
        'status': False,
        'message': 'Data error',
    }

    if type(domain) is str and len(domain) > 0:
        pre = re.compile(
            r'^(?=.{1,253}$)(?!.*\.\..*)(?!\..*)([a-zA-Z0-9-]{,63}\.){,127}[a-zA-Z0-9-]{1,63}$')
        if not pre.match(domain):
            result['message'] = f"Domain name {domain} is invalid"
        else:
            result['status'] = True
            result['message'] = f"Domain name {domain} is valid"

    return result


