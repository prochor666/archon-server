from archon import app, compat, utils
import json
#from archon.api.auth import auth as login
from archon.api import assets, auth, common, db, devices, network, remote, system, users 
from archon.auth import auth as authorization

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from archon.api import openapi_notes

compat.check_version()
app.mode = 'http'

openapi_notes

webapp = FastAPI(**openapi_notes.read())

webapp.add_middleware(
    CORSMiddleware,
    allow_origins=app.config['hosts']['origins'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

def api_init(request: Request) -> dict:
    result = is_authorized(request)
    set_client_ip(request)
    # app.store['user'] = users._get_system_user()
    return result


def is_authorized(request: Request) -> dict:
    token = request.headers.get('Authorization')
    authResult = authorization.authorization_process(token = str(token))
    app.store['user'] = authResult
    users._secure_auth_user()
    return authResult


def set_client_ip(request: Request) -> str: 
    app.store['client_ip'] = str(request.client.host)

    if request.headers.get('X-Forwarded-For') != None:
        app.store['client_ip'] = request.headers.get('X-Forwarded-For')

    if request.headers.get('X-Real-Ip') != None:
        app.store['client_ip'] = request.headers.get('X-Real-Ip')
    return app.store['client_ip']


def bad_status(message: str = '') -> dict:
    return {
        'status': False,
        'message': message,
    }


# System HW/SW
@webapp.get("/api/v1/search", tags=['Search'], status_code=status.HTTP_200_OK)
async def respond(
    response: Response, 
    request: Request,
    search: str = '') -> dict:

    api_init(request)
    endpoint = 'search'

    match endpoint:
        case 'search':
            return assets._search({
                'search': search
            })
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {str(request.method)}/{endpoint} not enabled")


# Common info
@webapp.get("/api/v1/common/{endpoint}", tags=['Common'], status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request) -> dict:

    api_init(request)
    endpoint = str(endpoint).replace('/', '')

    match endpoint:
        case 'test':
            return common._test()
        case 'get_enums':
            return common._get_enums()
        case 'countries':
            return common._countries()
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {str(request.method)}/{endpoint} not enabled")


# System HW/SW
@webapp.get("/api/v1/system/{endpoint}", tags=['System'], status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request) -> dict:

    api_init(request)
    endpoint = str(endpoint).replace('/', '')

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
            return bad_status(f"Endpoint {str(request.method)}/{endpoint} not enabled")


# Network
@webapp.get("/api/v1/network/{endpoint}", tags=["Network"], status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request,
    domain: str = '',
    dns_records: str = '',
    ip: str = '',
    ports: str = '') -> dict:

    api_init(request)
    endpoint = str(endpoint).replace('/', '')

    match endpoint:
        case 'client_ip':
            return network._client_ip()
        case 'domain_info':
            return network._domain_info({
                'domain': domain,
                'dns_records': dns_records
            })
        case 'scan_ip':
            return network._scan_ip({
                'ip': ip,
                'ports': ports
            })
        case 'ip':
            return network._ip()
        case 'scan_all_interfaces':
            return network._scan_all_interfaces()
        case 'ssh_keys':
            return network._ssh_keys()
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {str(request.method)}/{endpoint} not enabled")


# Network
@webapp.get("/api/v1/remote/{endpoint}", tags=["Remote"], status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request,
    server_id: str = '') -> dict:

    api_init(request)
    endpoint = str(endpoint).replace('/', '')

    match endpoint:
        case 'test_connection':
            return remote._test_connection({
                'server_id': server_id
            })
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {str(request.method)}/{endpoint} not enabled")



# Validation
@webapp.get("/api/v1/validation/{endpoint}", tags=["Validation"], status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    domain: str = '',
    email: str = '',
    ip: str = '') -> dict:
    
    api_init(request)
    endpoint = str(endpoint).replace('/', '')

    match endpoint:
        case 'email':
            return common._is_email({
                'email': email
            })
        case 'ip':
            return common._is_ip({
                'ip': ip
            })
        case 'domain':
            return network._validate_domain({
                'domain': domain
            })
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {str(request.method)}/{endpoint} not enabled")

# Browser
@webapp.get("/api/v1/{endpoint}", tags=["Browse"], status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    _filter: str = '',
    _sort: str = '') -> dict:

    authorization = api_init(request)
    endpoint = str(endpoint).replace('/', '')

    data = {
        'filter': _filter,
        'sort': _sort
    }

    match endpoint:
        case 'auth':
            return authorization
        case 'devices': 
            return devices._devices(data)
        case 'users':
            return users._users(data)
        case 'servers':
            return assets._servers(data)
        case 'scripts':
            return assets._scripts(data)
        case 'sites':
            return assets._sites(data)
        case 'notifications':
            return assets._notifications(data)
        case 'items':
            return assets._items(data)
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {str(request.method)}/{endpoint} not X enabled")


# One item
@webapp.get("/api/v1/{endpoint}/{id}", tags=["Detail"], status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    id: str) -> dict:

    api_init(request)
    endpoint = str(endpoint).replace('/', '')
    _id = str(id).replace('/', '')

    match endpoint:
        case 'users':
            return users._load_one(_id)
        case 'devices':
            return devices._device_one(_id)
        case 'device_pair':
            return devices._device_pair(_id)
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
            return bad_status(f"Endpoint {str(request.method)}/{endpoint} not Y enabled")


# Auth
@webapp.post("/api/v1/auth/{endpoint}", tags=["Auth"], status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    data: dict = {}) -> dict:
    
    api_init(request)
    endpoint = str(endpoint).replace('/', '')
    
    match endpoint:
        case 'activate':
            return auth._activate(data)
        case 'recover':
            return auth._recover(data)
        case 'pair': 
            app.store['user']['data'] = users._get_system_user()
            users._secure_auth_user()
            return devices._device_pair(data)
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {str(request.method)}/{endpoint} not enabled")



# New item
@webapp.post("/api/v1/{endpoint}", tags=["Create"], status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    data: dict) -> dict:
    
    api_init(request)
    endpoint = str(endpoint).replace('/', '')

    match endpoint:
        case 'users':
            return users._user_create(data)
        case 'devices':
            return devices._device_create(data)
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
            return bad_status(f"Endpoint {str(request.method)}/{endpoint} not enabled")


# Modify item
@webapp.put("/api/v1/{endpoint}/{id}", tags=["Modify"], status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    id: str,
    data: dict) -> dict:
    
    api_init(request)
    endpoint = str(endpoint).replace('/', '')
    data['id'] = str(id).replace('/', '')
    
    match endpoint:
        case 'users':
            return users._user_modify(data)
        case 'devices':
            return devices._device_modify(data)
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
            return bad_status(f"Endpoint {str(request.method)}/{endpoint} not enabled")


# Delete item
@webapp.delete("/api/v1/{endpoint}/{id}", tags=["Delete"], status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    id: str) -> dict:

    api_init(request)
    endpoint = str(endpoint).replace('/', '')
    _id = str(id).replace('/', '')

    match endpoint:
        case 'users':
            return users._user_delete(_id)
        case 'devices':
            return devices._device_delete(_id)
        case 'servers':
            return assets._server_delete(_id)
        case 'scripts':
            return assets._script_delete(_id)
        case 'sites':
            return assets._site_delete(_id)
        case 'items':
            return assets._item_delete(_id)
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {str(request.method)}/{endpoint} not enabled")


# Web routing
@webapp.get("/{page}/", tags=["Page"], status_code=status.HTTP_200_OK)
async def respond(
    page: str,
    response: Response, 
    request: Request, ) -> dict:

    api_init(request)
    page = str(page).replace('/', '')

    match page:
        case 'templates':
            return HTMLResponse(content=f"""<html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Hey! Page {page} is here.</h1>
        </body>
    </html>""", status_code=status.HTTP_200_OK)
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Page {page} not enabled")