from archon import app, compat, utils
import json
#from archon.api.auth import auth as login
from archon.api import assets, auth, common, db, network, remote, system, users 
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
@webapp.get("/api/v1/common/{endpoint}", tags=['Common'], status_code=status.HTTP_200_OK)
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
@webapp.get("/api/v1/system/{endpoint}", tags=['System'], status_code=status.HTTP_200_OK)
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
    domain: str = '',
    dns_records: str = '',
    ip: str = '',
    ports: str = '') -> dict:

    set_client_ip(request)
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
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {endpoint} not enabled")


# Validation
@webapp.get("/api/v1/validation/{endpoint}", status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    domain: str = '',
    email: str = '',
    ip: str = '') -> dict:
    
    set_client_ip(request)
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
            return bad_status(f"Endpoint {endpoint} not enabled")

# Browser
@webapp.get("/api/v1/{endpoint}", status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request, 
    _filter: str = '',
    _sort: str = '') -> dict:

    set_client_ip(request)

    data = {
        'filter': _filter,
        'sort': _sort
    }
    
    match endpoint:
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

    match endpoint:
        case 'users':
            return users._user_delete(_id)
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
            return bad_status(f"Endpoint {endpoint} not enabled")


# Web routing
@webapp.get("/{page}/", status_code=status.HTTP_200_OK)
async def respond(
    page: str,
    response: Response, 
    request: Request, ) -> dict:

    set_client_ip(request)
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