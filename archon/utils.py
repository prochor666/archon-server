import os
import glob
from datetime import timezone, datetime
import re
import random
import ipaddress
import string
from archon import app, colors
import dns.resolver


def database_check() -> dict:

    driver = app.config['db_driver']
    output = {
        'db_config': f"{app.config['db'][driver]['host']}:{str(app.config['db']['mongodb']['port'])}"
    }

    try:
        db_info = app.db_client.server_info()
        db_db = app.db_client.list_database_names()
        output['db_instance'] = db_info
        output['databases'] = db_db
        output['status'] = True
        output['message'] = f"MongoDb version {db_info['version']} connected, verbose info:"

    except Exception as error:
        output['status'] = False
        output['message'] = str(error)

    return output


def byte_size(bytes: float, suffix: str ="B") -> str:
    factor = 1024
    # https://en.wikipedia.org/wiki/Metric_prefix
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z", "Y", "R", "Q"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor
    return "Unknown"


def decimal_size(num: float, suffix: str ="Hz") -> str:
    factor = 1000
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z", "Y", "R", "Q"]:
        if num < factor:
            return f"{num:.2f} {unit}{suffix}"
        num /= factor
    return "Unknown"


def replace_all(text: str, r: dict ={}) -> str:
    for i, j in r.items():
        text = text.replace(i, j)
    return text


def in_dict(d: dict, key: str) -> bool:
    if type(d) is dict and key in d.keys():
        return True
    return False


def is_username(username: str = '') -> bool:
    return all(ch.isalnum() or ch.isspace() for ch in str(username))


def now() -> str:
    dt_now = datetime.now(tz=timezone.utc).isoformat()
    return str(dt_now)


def app_root() -> str:
    p = os.path.dirname(os.path.abspath(__file__))
    return strip_end(p, f"{os.path.sep}core")


def strip_end(text: str, suffix: str) -> str:
    if suffix and text.endswith(suffix):
        return text[:-len(suffix)]
    return text


def format_response(status: bool, text: str) -> str:
    return f"""{colors.fg('Ok', 'LIGHTGREEN_EX')}: {text}""" if status == True else f"""{colors.fg('Error', 'red')}: {text}"""


def ark(obj: dict = {}, key: str = '', default: str = ''):
    return obj[key] if len(key) > 0 and key in obj.keys() else default


def validate_data_pass(d: dict) -> dict:
    result = {}
    for k in d.keys():
        v = d[k]
        if v != None:
            result[k] = v
    return result


def ip_valid(ip: str) -> dict:
    r = {
        'status': False,
        'ip': ip,
        'version': 0,
        'message': 'Invalid input',
        'is_global': False,
        'is_multicast': False,
        'is_private': False,
        'is_reserved': False,
        'is_loopback': False,
        'is_link_local': False,
    }
    try:
        i = ipaddress.ip_address(ip)
        if i.version == 4 or i.version == 6:
            r['status'] = True
            r['message'] = 'IP validated'
        r['version'] = i.version
        r['is_global'] = i.is_global
        r['is_multicast'] = i.is_multicast
        r['is_private'] = i.is_private
        r['is_reserved'] = i.is_reserved
        r['is_loopback'] = i.is_loopback
        r['is_link_local'] = i.is_link_local
        return r
    except Exception as e:
        r['message'] = str(e)
        return r


def mac_valid(mac: str) -> dict:
    r = {
        'status': False,
        'mac': mac,
        'message': 'Invalid input',
    }
    if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
        r['status'] = True
        r['message'] = 'Valid MAC address'
    return r

def domain_dns_info(domain: str, record_filter: list = []) -> list:
    record_types = [
        'A',
        'AAAA',
        'AFSDB',
        'ALIAS',
        'APL',
        'CAA',
        'CDNSKEY',
        'CDS',
        'CERT',
        'CNAME',
        'CSYNC',
        'DHCID',
        'DLV',
        'DNAME',
        'DNSKEY',
        'DS',
        'EUI48',
        'EUI64',
        'HINFO',
        'HIP',
        'IPSECKEY',
        'KEY',
        'KX',
        'LOC',
        'MX',
        'NAPTR',
        'NS',
        'NSEC',
        'NSEC3',
        'NSEC3PARAM',
        'OPENPGPKEY',
        'PTR',
        'RRSIG',
        'RP',
        'SIG',
        'SMIMEA',
        'SOA',
        'SRV',
        'SSHFP',
        'TA',
        'TKEY',
        'TLSA',
        'TSIG',
        'TXT',
        'URI',
        'ZONEMD',
        'SVCB',
        'HTTPS',
    ]
    result = []

    if type(record_filter) is list and len(record_filter) > 0:
        record_types = record_filter

    for record_type in record_types:
        try:
            dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
            dns.resolver.default_resolver.nameservers=app.config['dns_resolver']['nameservers']

            for rdata in dns.resolver.resolve(domain, record_type): # type: ignore
                result.append({'type': record_type, 'value': rdata.to_text()})
        except Exception as e:
            pass

    return result


def detect_object_changes(keys: list, origin: dict, new: dict) -> bool:
    for key in keys:
        if key in origin.keys() and key in new:
            if origin[key] != new[key]:
                return True
        else:
            pass

    return False


def list_ssh_keys() -> list:
    ssh_dir = f"{os.path.expanduser('~')}{os.path.sep}.ssh{os.path.sep}*"
    files = []
    for f in glob.glob(ssh_dir):
        filename, file_extension = os.path.splitext(f)
        if os.path.isfile(f) and os.path.basename(filename) not in ['known_hosts', 'authorized_keys', 'config'] and file_extension not in ['.pub','.key']:
            files.append(f)

    return files


def file_save(file: str, content: str =' ') -> bool:
    fh = open(file, 'w')
    fh.write(content)
    fh.close()
    return True


def eval_key(key: str, data: dict = {}, data_type: str = 'str') -> str | int | float | dict | list | bool | None:
    if data_type == 'str':
        return '' if key not in data.keys() or type(data[key]) is not str else data[key]

    if data_type == 'int':
        return 0 if key not in data.keys() or type(data[key]) is not int else data[key]

    if data_type == 'float':
        return 0 if key not in data.keys() or type(data[key]) is not float else data[key]

    if data_type == 'dict':
        return {} if key not in data.keys() or type(data[key]) is not dict else data[key]

    if data_type == 'list':
        return [] if key not in data.keys() or type(data[key]) is not list else data[key]

    if data_type == 'bool':
        return False if key not in data.keys() or type(data[key]) is not bool else data[key]

    if data_type == 'ipv4':
        return '' if key not in data.keys() or type(data[key]) is not str or ip_valid(data[key])['version'] != 4 else str(data[key])

    if data_type == 'ipv6':
        return '' if key not in data.keys() or type(data[key]) is not str or ip_valid(data[key])['version'] != 6 else str(data[key])
    
    return None


def apply_filter(data_pass: dict) -> dict:
    data_filter = {}
    data_sort = ['Id', 1]
    data_exclude = None

    if type(data_pass) is dict:

        if 'filter' in data_pass.keys() and type(data_pass['filter']) is dict and len(data_pass['filter']) > 0:
            data_filter = data_pass['filter']

        if 'filter' in data_pass.keys() and type(data_pass['filter']) is list and len(data_pass['filter']) > 0:
            data_filter = filter_to_dict(data_pass['filter'])

        if 'filter' in data_pass.keys() and type(data_pass['filter']) is str and len(data_pass['filter']) > 0:
            df = data_pass['filter'].split(':')
            if len(df) == 2:
                data_filter = {df[0]: df[1]}

        if 'sort' in data_pass.keys() and type(data_pass['sort']) is list and len(data_pass['sort']) == 2:
            data_sort = data_pass['sort']

        if 'sort' in data_pass.keys() and type(data_pass['sort']) is str and len(data_pass['sort']) > 0:
            df = data_pass['sort'].split(':')
            if len(df) == 2:
                data_sort = [df[0], df[1]]

        if 'exclude' in data_pass.keys() and type(data_pass['exclude']) is dict and len(data_pass['exclude']) > 0:
            data_exclude = data_pass['exclude']


    return {
        'filter': data_filter,
        'sort': data_sort,
        'exclude': data_exclude
    }


def filter_to_dict(data_filter: list) -> dict:
    d = {}
    # return filter_data
    for f in data_filter:
        s = f.split(':')
        if len(s) == 2:
            d[s[0]] = s[1]

    return d


def index_eval() -> dict:
    user_indexes = app.db['users'].index_information()
    server_indexes = app.db['servers'].index_information()
    site_indexes = app.db['sites'].index_information()
    script_indexes = app.db['scripts'].index_information()
    device_indexes = app.db['devices'].index_information()
    item_indexes = app.db['items'].index_information()

    r = 'all created'

    if 'name_-1_ipv4_-1_ipv6_-1' not in server_indexes:
        r = app.db['servers'].create_index(
            [('name', -1), ('ipv4', -1), ('ipv6', -1)])

    if 'name_-1' not in device_indexes:
        r = app.db['devices'].create_index(
            [('name', -1)])

    if 'name_-1' not in script_indexes:
        r = app.db['scripts'].create_index(
            [('name', -1)])

    if 'username_-1_email_-1_firstname_-1_lastname_-1' not in user_indexes:
        r = app.db['users'].create_index(
            [('username', -1), ('email', -1), ('firstname', -1), ('lastname', -1)])

    if 'name_-1_domain_-1_dev_domain_-1' not in site_indexes:
        r = app.db['sites'].create_index(
            [('name', -1), ('domain', -1)])

    if 'name_-1_type_-1_ref_-1' not in item_indexes:
        r = app.db['items'].create_index(
            [('name', -1), ('type', -1), ('ref', -1)])

    return {
        'user_indexes': app.db['users'].index_information(),
        'server_indexes': app.db['servers'].index_information(),
        'site_indexes': app.db['sites'].index_information(),
        'script_indexes': app.db['scripts'].index_information(),
        'device_indexes': app.db['devices'].index_information(),
        'item_indexes': app.db['items'].index_information(),
    }


def br2nl(s: str) -> str:
    return re.sub('<br\\s*?>', "\n", str(s))


def nl2br(s: str) -> str:
    return '<br />'.join(s.split("\n"))


def dos2unix(s: str) -> str:
    return str(s).replace('\r\n', '\n')


def rnd(length: int = 7, digits_only: bool = False):
    base = string.digits
    if digits_only == False:
        base = string.digits +  string.ascii_letters
    rstr =  ''.join(random.choice(base) for i in range(length))
    return rstr


def tag_parse(tag: str, raw: str) -> str:
    result = re.findall(
        f"<{tag}>(.*?)</{tag}>", raw, re.DOTALL)
    if len(result) > 0:
        return result[0]
    return ''


# 3rd party
# thx to: https://www.calebthorne.com/blog/python/2012/06/08/python-strip-tags
def strip_tags(string: str, allowed_tags: str ='') -> str:
    allowed_pattern = ''
    if allowed_tags != '':
        # Get a list of all allowed tag names.
        allowed_tags_list = re.sub(r'[\\/<> ]+', '', allowed_tags).split(',')
        
        for s in allowed_tags_list:

            if s == '':
                continue
                # Add all possible patterns for this tag to the regex.

            if allowed_pattern != '':
                allowed_pattern += '|'

            allowed_pattern += '<' + s + ' [^><]*>$|<' + s + '>|'

    # Get all tags included in the string.
    all_tags = re.findall(r'<]+>', string, re.I)

    for tag in all_tags:
        # If not allowed, replace it.
        if type(allowed_pattern) is str and not re.match(allowed_pattern, tag, re.I):
            string = string.replace(tag, '')
        else:
            # If no allowed tags, remove all.
            string = re.sub(r'<[^>]*?>', '', string)

    return string
