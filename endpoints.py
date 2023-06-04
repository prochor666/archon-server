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


# Common info
@webapp.get("/api/v1/common/{endpoint}", status_code=status.HTTP_200_OK)
async def respond(
    endpoint: str,
    response: Response, 
    request: Request) -> dict:

    set_client_ip(request)

    match endpoint:
        case 'test':
            return common._test({
                'test': 'Ok'
            })
        case 'get_enums':
            return common._get_enums()
        case '_countries':
            return common._countries()
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
        case 'system':
            return system._system()
        case 'network':
            return system._network()
        case 'cpu':
            return system._cpu()
        case 'memory':
            return system._memory()
        case 'disk':
            return system._disk()
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
@webapp.get("/api/v1/{endpoint}/{id}", status_code=status.HTTP_200_OK)
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
            return users._users({
                'filter': {
                    'id': _id
                }
            })
        case 'servers':
            return assets._servers({
                'filter': {
                    'id': _id
                }
            })
        case 'scripts':
            return assets._scripts({
                'filter': {
                    'id': _id
                }
            })
        case 'sites':
            return assets._sites({
                'filter': {
                    'id': _id
                }
            })
        case 'items':
            return assets._items({
                'filter': {
                    'id': _id
                }
            })
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
            return users._create_user()
        case 'servers':
            return assets._create_server(data)
        case 'scripts':
            return assets._create_script(data)
        case 'sites':
            return assets._create_site(data)
        case 'items':
            return assets._create_item(data)
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
            return users._modify_user(data)
        case 'servers':
            return assets._modify_server(data)
        case 'scripts':
            return assets._modify_script(data)
        case 'sites':
            return assets._modify_site(data)
        case 'items':
            return assets._modify_item(data)
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
            return users._delete_user(data)
        case 'servers':
            return assets._delete_server(data)
        case 'scripts':
            return assets._delete_script(data)
        case 'sites':
            return assets._delete_site(data)
        case 'items':
            return assets._delete_item(data)
        case _:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return bad_status(f"Endpoint {endpoint} not enabled")