from archon import app, compat, utils
#from archon.api.auth import auth as login
from archon.api import assets, auth, common, db, network, remote, system, users 
from archon.auth import auth as authorization

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

compat.check_version()
app.mode = 'http'

webapp = FastAPI()

webapp.add_middleware(
    CORSMiddleware,
    allow_origins=app.config['hosts']['origins'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def is_authorized(request):
    app.store['user'] = authorization.authorization_process(
                            request.headers.get('Authorization'))
    return app.store['user']


def set_client_ip(request): 
    app.store['client_ip'] = str(request.client.host)

    if request.headers.get('X-Forwarded-For') != None:
        app.store['client_ip'] = request.headers.get('X-Forwarded-For')

    if request.headers.get('X-Real-Ip') != None:
        app.store['client_ip'] = request.headers.get('X-Real-Ip')
    return app.store['client_ip']


def bad_status(message = ''):
    return {
        'status': False,
        'message': message,
    }


# Common info
@webapp.get("/api/v1/common/{endpoint}", status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request) -> dict:

    set_client_ip(request)
    
    match endpoint:
        case 'test':
            return common._test()
        case 'get_enums':
            return common._get_enums()
        case 'countries':
            return common._countries()
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {endpoint} not enabled")


# System HW/SW
@webapp.get("/api/v1/system/{endpoint}", status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request) -> dict:

    set_client_ip(request)

    match endpoint:
        case 'os':
            return system._os()
        case 'network':
            return system._network()
        case 'cpu':
            return system._cpu()
        case 'memory':
            return system._memory()
        case 'disk':
            return system._disk()
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {endpoint} not enabled")


# Network
@webapp.get("/api/v1/network/{endpoint}", status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request,
    domain: str = None,
    ip: str = None,
    ports: str = None,
    dns_records: str = None,
    ttl: str = None) -> dict:

    set_client_ip(request)
    endpoint = str(endpoint).replace('/', '')

    match endpoint:
        case 'client_ip':
            return network._client_ip()
        case 'domain_info':
            return network._domain_info(domain, dns_records)
        case 'scan_ip':
            return network._scan_ip(ip, ports,ttl)
        case 'ip':
            return network._ip()
        case 'scan_all_interfaces':
            return network._scan_all_interfaces(ports, ttl)
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {endpoint} not enabled")


# Validation
@webapp.get("/api/v1/validation/{endpoint}", status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    ip: str = None,
    email: str = None,
    domain: str = None) -> dict:
    
    set_client_ip(request)
    endpoint = str(endpoint).replace('/', '')

    match endpoint:
        case 'email':
            return common._is_email(email)
        case 'ip':
            return common._is_ip(ip)
        case 'domain':
            return network._validate_domain(domain)
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {endpoint} not enabled")

# Browser
@webapp.get("/api/v1/{endpoint}", status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    item_type: str = '', 
    filter: str = '', 
    sort: str = '') -> dict:

    set_client_ip(request)

    match endpoint:
        case 'users':
            return users._users({
                'filter': filter,
                'sort': sort,
            })
        case 'servers':
            return assets._servers({
                'filter': filter,
                'sort': sort,
            })
        case 'scripts':
            return assets._scripts({
                'filter': filter,
                'sort': sort,
            })
        case 'sites':
            return assets._sites({
                'filter': filter,
                'sort': sort,
            })
        case 'notifications':
            return assets._notifications({
                'filter': filter,
                'sort': sort,
            })
        case 'items':
            return assets._items({
                'item_type': item_type,
                'filter': filter,
                'sort': sort,
            })
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {endpoint} not enabled")


# One item
@webapp.get("/api/v1/{endpoint}/{_id}", status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    _id: str) -> dict:

    set_client_ip(request)
    endpoint = str(endpoint).replace('/', '')
    _id = str(_id).replace('/', '')

    match endpoint:
        case 'users':
            return users._load_one(_id)
        case 'servers':
            return assets._server_one(_id)
        case 'scripts':
            return assets._script_one(_id)
        case 'sites':
            return assets._site_one(_id)
        case 'items':
            return assets._item_one(_id)
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {endpoint} not enabled")


# New item
@webapp.post("/api/v1/{endpoint}", status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    data: dict) -> dict:
    
    set_client_ip(request)
    endpoint = str(endpoint).replace('/', '')

    match endpoint:
        case 'users':
            return users._user_create(data)
        case 'servers':
            return assets._server_create(data)
        case 'scripts':
            return assets._script_create(data)
        case 'sites':
            return assets._site_create(data)
        case 'items':
            return assets._item_create(data)
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {endpoint} not enabled")


# Modify item
@webapp.put("/api/v1/{endpoint}/{id}", status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    id: str,
    data: dict) -> dict:
    
    set_client_ip(request)
    endpoint = str(endpoint).replace('/', '')
    _id = str(id).replace('/', '')
    data.id = _id

    match endpoint:
        case 'users':
            return users._user_modify(data)
        case 'servers':
            return assets._server_modify(data)
        case 'scripts':
            return assets._script_modify(data)
        case 'sites':
            return assets._site_modify(data)
        case 'items':
            return assets._item_modify(data)
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {endpoint} not enabled")


# Delete item
@webapp.delete("/api/v1/{endpoint}/{id}", status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    id: str) -> dict:
    
    set_client_ip(request)
    endpoint = str(endpoint).replace('/', '')
    _id = str(id).replace('/', '')
    data = {
        'id': _id
    }

    match endpoint:
        case 'users':
            return users._user_delete(data)
        case 'servers':
            return assets._server_delete(data)
        case 'scripts':
            return assets._script_delete(data)
        case 'sites':
            return assets._site_delete(data)
        case 'items':
            return assets._item_delete(data)
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {endpoint} not enabled")