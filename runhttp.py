import json
from archon import app, compat
#from archon.api.auth import auth as login
from archon.api import assets, auth, common, db, network, remote, system,  users 
from archon.auth import auth as authorization

from typing import Union
from fastapi import FastAPI, Request, Header, Response, status
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


@webapp.get("/")
@webapp.get("/api")
@webapp.get("/api/v1")
def read_root(request: Request, response: Response):
    response.status_code = status.HTTP_400_BAD_REQUEST
    return common._about()


@webapp.get("/api/v1/{endpoint}", status_code=status.HTTP_200_OK)
@webapp.get("/api/v1/{endpoint}/{id}", status_code=status.HTTP_200_OK)
@webapp.post("/api/v1/{endpoint}", status_code=status.HTTP_201_CREATED)
@webapp.put("/api/v1/{endpoint}/{id}", status_code=status.HTTP_200_OK)
@webapp.patch("/api/v1/{endpoint}/{id}", status_code=status.HTTP_200_OK)
@webapp.delete("/api/v1/{endpoint}/{id}", status_code=status.HTTP_200_OK)
async def respond(endpoint: str, request: Request, response: Response, id: str = '') -> dict:
    
    # Check request headers
    # print(str(type(request.client)))
    app.store['client_ip'] = str(request.client.host)

    if request.headers.get('X-Forwarded-For') != None:
        app.store['client_ip'] = request.headers.get('X-Forwarded-For')

    if request.headers.get('X-Real-Ip') != None:
        app.store['client_ip'] = request.headers.get('X-Real-Ip')

    endpoint = str(endpoint).replace('/', '')
    _id = str(id).replace('/', '')

    reason = f"API endpoint {endpoint} is not supported"
    module_status = False
    result = None
    
    logged = authorization.authorization_process(endpoint, request.method, request.headers.get('Authorization')) # type: ignore
    
    data_pass = {}
    
    #if endpoint != None and endpoint in dir(api):
    if endpoint != None and endpoint in app.config['api']['rest'].keys():
        reason = f"API route: {endpoint} method {request.method} not allowed"

        #if request.method in ['POST', 'PUT', 'PATCH'] and \
        if request.method in app.config['api']['rest'][endpoint]['methods'].keys() and \
            request.headers.get('Content-type') != None and \
            str(request.headers.get('Content-type')).startswith('application/json'):

            reason = f"API route: {endpoint} method {request.method} allowed"
                
            if request.method == 'GET':
                request_data = request.get
            else: 
                request_data = await request.json()

            if type(request_data): 
                request_data.update(data_pass)

        if  type(data_pass) != dict:
            data_pass = {
                'filter': {}
            }

        if  len(_id) > 0:
            {
                'filter': {
                    'id': _id
                }
            }.update(data_pass)

        result = logged
        app.store['user'] = logged

        if logged['status'] == True:
            # Start api request passing
            module_status = True

            if endpoint != 'login':
                parsed_decorator = app.config['api']['rest'][endpoint]['methods'][request.method]['decorator'].split('.')
                module = parsed_decorator[0]
                method = parsed_decorator[1]

                obj = globals()
                result = getattr(obj[module], method)(data_pass)
        else:
            response.status_code = status.HTTP_401_UNAUTHORIZED
    else: 
        response.status_code = status.HTTP_400_BAD_REQUEST

    res = {
        'api': f"{app.config['name']} REST api 1.0",
        'endpoint_status': module_status,
        'reason': reason,
        'result': result,
        'data_pass': data_pass,
        #'auth': logged,
        #'id': 0 if _id == 'None' else _id,
    }

    return res