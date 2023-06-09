import time
import datetime
import socket
from archon import app, utils
from archon.system import device


def device_ip() -> list:
    netifs = device.network_info()
    ips = []
    for netif in netifs:
        # if netifs[netif]['ipv4'] != '-':
        #    ips.append(netifs[netif]['ipv4'])
        ips.append(netifs[netif]['ipv4'])
        ips.append(netifs[netif]['ipv6'])
    return ips


def ssh_port() -> int:
    return 22


def scan_all_interfaces(ports: list = [20, 21, 22, 23, 8080, 80, 443, 3389], ttl: float = None) -> list:
    ips = device_ip()
    result = []
    if type(ips) is list:
        for ip in ips:
            result.append(scan_ip(ip, ports, ttl))
    return result


def resolve_socket(ip_version: int = 4):
    return socket.socket(socket.AF_INET6, socket.SOCK_STREAM) if ip_version == 6 else socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def scan_ip(ip: str, ports: list = [21, 22, 23, 80, 443, 3306], ttl: float = None) -> dict:
    ip_valid = utils.ip_valid(ip)
    
    start_time = time.time()
    ip_target = str(ip_valid['ip'])
    ip_version = int(ip_valid['version'])
    
    if type(ttl) is not float:
        if 'scan_ip' in app.config and 'ttl' in app.config['scan_ip'] and type(app.config['scan_ip']["ttl"]) in [float, int]:
            ttl = app.config['scan_ip']["ttl"]

    result = {
        'ip': ip,
        'ports': {},
        'scan_result': "Failed, no init",
        'scan_status': False,
        'time': 0,
        'ttl': ttl
    }

    try:
        for port in ports:

            try:
                port = int(port)
                sock = resolve_socket(ip_version)
                sock.settimeout(ttl)
                scan_result = sock.connect_ex((ip_target, port))

                if scan_result == 0:
                    result['ports'][port] = True
                else:
                    result['ports'][port] = False
                sock.close()

            except Exception as e:
                result['ports'][port] = "Exception type %s" % (e)

        result['scan_result'] = "Scanned"
        result['scan_status'] = True

    except KeyboardInterrupt:
        result['scan_result'] = "You pressed Ctrl+C"
        result['scan_status'] = False
        result['ttl'] = ttl

    delta = time.time() - start_time
    result['time'] = str(datetime.timedelta(seconds=delta))
    return result
