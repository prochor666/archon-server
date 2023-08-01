from http.client import HTTPSConnection
from datetime import datetime, timezone, timedelta
from archon import app, utils
import ssl, json, pytz

def guard(data_pass: dict = {}) -> dict:
    domains = utils.ark(data_pass, 'domains', [])
    result = {
        'status': False,
        'message': 'No domain defined',
        'domains': [],
    }
    if len(domains) > 0:
        for host in domains:
            fire(host)
        result['domains'] = verify_results()
        #dump_result(result)
        result['status'] = True
        ld = 'domains'
        if len(domains) == 1:
            ld = 'domain'
        result['message'] = f"{len(domains)} {ld} analyzed"
        
    return result


def create_custom_HTTPSConnection(host: str) -> object:
    class CustomHTTPSConnection(HTTPSConnection, object):
        def connect(self):
            try:
                super(CustomHTTPSConnection, self).connect()
                try: 
                    cert = self.sock.getpeercert()
                    app.mem.r(f"{host}", { 'certificate': cert, 'valid': True})
                except Exception as error:
                    app.mem.r(f"{host}", { 'error': f"Exception: {str(error)}" })
            except ConnectionError:
                app.mem.r(f"{host}", { 'error': f"ConnectionError: {str(ConnectionError)}" })

    context = ssl.create_default_context()
    context.check_hostname = False
    return CustomHTTPSConnection(host=host, context=context)


def verify_results() -> dict:
    memo = app.app.mem.a()
    result = {
        'domains': [],
    }
    for record_key in memo.keys():
        record = memo[record_key]
        item = {
            'domain': record_key,
            'certificate': {},
            'status': False,
            'notify': False,
            'message': '',
        }
        # Write common message

        if type(record) is dict and 'error' in record.keys():
            item['notify'] = True
            item['message'] = record['error']

        before = datetime.now(timezone.utc)
        after = datetime.now(timezone.utc)
        if type(record) is dict and 'certificate' in record.keys():
            for k in record['certificate'].keys():
                if type(record['certificate'][k]) in [tuple, list]:
                    a = to_dict(record['certificate'][k])
                    item['certificate'][k] = a 
                else: 
                    item['certificate'][k] = record['certificate'][k]
                    
                    if k  == 'notBefore':
                        before = check_date(record['certificate'][k])
                        item['certificate'][k] = str(before)
                    if k == 'notAfter':
                        after = check_date(record['certificate'][k])
                        item['certificate'][k] = str(after)
                        
            if 'notBefore' in item['certificate'] and 'notAfter' in item['certificate']:
                v = validate_cert_date(before, after)
                
                item['notify'] = v['notify']
                item['message'] = v['message']
                item['status'] = v['ok']
                
        result['domains'].append(item)
    return result


def check_date(ds: str): 
    return datetime.strptime(ds, '%b %d %H:%M:%S %Y %Z')


def validate_cert_date(before: datetime, after: datetime, days: int = 7) -> dict:
    utc=pytz.UTC
    today = datetime.now(timezone.utc)
    before = utc.localize(before)
    after = utc.localize(after)
    result = {
        'ok': True,
        'notify': False,
        'message': f"Certificate is ok (expire on {str(after)} UTC)"
    }
    
    if today < before or today > after:
        result['notify'] = True
        result['message'] = f"Certificate expired on {str(after)} UTC"
    if after < today + timedelta(days = days):
        result['notify'] = True
        result['message'] = f"Certificate is ok, but expire soon (less then {days} days) {str(after)} UTC"
    return result


def dump_result(result: dict):
    utils.file_save('result.json', json.dumps(result, indent=4))


def to_dict(data: list | tuple) -> dict:
    r = {}
    for i in range(len(data)):
        if type(data[i]) in [tuple, list]:
            if len(data[i]) == 1:
                if type(data[i][0]) in [tuple, list]:
                    r[data[i][0][0]] = data[i][0][1]
                else:
                    r[i] = data[i]
            else:
                r[data[i][0]] = data[i][1]
        else: 
            r[i] = data[i]
    return r


def fire(host: str):
    print(f"- {host}")
    conn = create_custom_HTTPSConnection(host)
    try:
        conn.request('GET', '/')
        conn.getresponse().read()
    except Exception as error:
        #print("Request error", error)
        app.mem.r(f"{host}", { 'error': f"CONNECTION: {str(error)}" })

