import re
import json
from bson.objectid import ObjectId
from archon import app, data, utils
from archon.models.servers import servers
from archon.models.scripts import scripts
from archon.models.notifications import notifications


def load(filter_data: dict | None = None, sort_data: dict | None = None, exclude_data: dict | None = None) -> list:
    finder = {
        'collection': 'sites',
        'filter': filter_data,
        'sort': sort_data,
        'exclude': exclude_data
    }
    return data.ex(finder)


def load_one(filter_data: dict) -> dict:
    finder = {
        'collection': 'sites',
        'filter': filter_data
    }
    return data.one(finder)


def modify(site_data: dict) -> dict:
    result = validator(site_data)

    if 'id' not in site_data.keys():
        result['message'] = 'Need id to modify site'
        result['status'] = False

    if len(str(site_data['id'])) != 24:
        result['message'] = 'Site id is invalid'
        result['status'] = False

    if result['status'] == True:

        if 'alias_domains' in site_data.keys() and type(site_data['alias_domains']) is str:
            site_data['alias_domains'] = site_data['alias_domains'].splitlines()

        if 'dev_domain' in site_data.keys() and len(site_data['dev_domain']) > 0:
            finder = load_one({
                '$and': [
                    {
                        '$or': [
                            {'name': site_data['name']},
                            {'domain': site_data['domain']},
                            {'dev_domain': site_data['dev_domain']}
                        ],
                    },
                    {
                        '_id': {
                            '$ne': ObjectId(site_data['id'])
                        }
                    }
                ]
            })

        else:
            finder = load_one({
                '$and': [
                    {
                        '$or': [
                            {'name': site_data['name']},
                            {'domain': site_data['domain']}
                        ],
                    },
                    {
                        '_id': {
                            '$ne': ObjectId(site_data['id'])
                        }
                    }
                ]
            })

        modify_site = load_one({
            '_id': ObjectId(site_data['id'])
        })

        if type(finder) is not dict and type(modify_site) is dict:
            _id = site_data.pop('id', None)
            site_data.pop('creator', None)
            site_data.pop('created_at', None)

            site = dict()
            site.update(modify_site)
            site.update(site_data)

            if 'home_dir' not in site.keys() or len(site['home_dir']) == 0:
                site['home_dir'] = site['domain']

            site['updated_at'] = utils.now()

            changed = utils.detect_object_changes([
                'name',
                'description',
                'server_id',
                'script_id',
                'publish',
                'domain',
                'dev_domain',
                'alias_domains',
                'owner',
            ], modify_site, site)

            sites = app.db['sites']

            site = site_model(site)
            sites.update_one(
                {'_id': ObjectId(_id)},
                {'$set': site})

            result['message'] = f"Site {site['name']} not modified"

            if changed == True:
                # Notification comes here
                result['message'] = f"Site {site['name']} modified"
                notifications.db(
                    'site', str(_id), f"Site {site['name']} was modified.", json.dumps(data.collect_one(site), indent=4))

            result['status'] = True
            result['changed'] = changed

        else:
            param_found = ''
            if type(finder) is dict and 'name' in finder.keys() and finder['name'] == site_data['name']:
                param_found = f"with name {site_data['name']}"
            if len(param_found) == 0 and type(finder) is dict and 'domain' in finder.keys() and finder['domain'] == site_data['domain']:
                param_found = f"with same domain {site_data['domain']}"
            if len(param_found) == 0 and type(finder) is dict and 'dev_domain' in finder.keys() and finder['dev_domain'] == site_data['dev_domain']:
                param_found = f"with same dev domain {site_data['dev_domain']}"

            result['status'] = False
            result['message'] = f"Site {param_found} already exists"

    return result


def insert(site_data: dict) -> dict:
    result = validator(site_data)

    if result['status'] == True:

        if 'alias_domains' in site_data.keys() and type(site_data['alias_domains']) is str:
            site_data['alias_domains'] = site_data['alias_domains'].splitlines()

        site = site_model(site_data)

        if type(site) is dict and 'dev_domain' in site.keys() and len(str(site['dev_domain'])) > 0:
            finder = load_one({
                '$or': [
                    {'name': str(site['name'])},
                    {'domain': str(site['domain'])},
                    {'dev_domain': str(site['dev_domain'])}
                ]
            })
        else:
            finder = load_one({
                '$or': [
                    {'name': str(site['name'])},
                    {'domain': str(site['domain'])}
                ]
            })


        if type(finder) is not dict:

            site_data.pop('id', None)
            site_data.pop('updated_at', None)

            site['created_at'] = utils.now()
            site['creator'] = app.config['user']['_id']
            site['home_dir'] = site['domain']

            sites = app.db['sites']
            _id = sites.insert_one(site)

            # Notification comes here
            html_message_data = {
                'app_full_name': app.config['name'],
                'username': app.config['user']['username'],
                'message': f"Site {site['name']} was created."
            }
            notifications.email('settings.notifications.sites',
                                'common-notification', f"{app.config['name']} - site created", html_message_data)

            notifications.db(
                'site', str(_id.inserted_id), f"Site {site['name']} was created.", json.dumps(data.collect_one(site), indent=4))

            result['status'] = True
            result['message'] = f"Site {site['name']} created"
        else:

            param_found = ''
            if finder['name'] == site['name']:
                param_found = f"with name {site['name']}"
            if len(param_found) == 0 and finder['domain'] == site['domain']:
                param_found = f"with same domain {site['domain']}"
            if len(param_found) == 0 and finder['dev_domain'] == site['dev_domain']:
                param_found = f"with same dev domain {site['dev_domain']}"

            result['status'] = False
            result['message'] = f"Site {param_found} already exists"

    return result


def delete(site_data: dict) -> dict:
    result = {
        'status': False,
        'message': 'Need id to delete site',
        'site_data': site_data
    }

    if 'id' in site_data.keys():
        sites = app.db['sites']
        r = sites.delete_one({'_id': ObjectId(site_data['id'])})
        result['delete_status'] = r.deleted_count
        result['status'] = False if r.deleted_count == 0 else True
        result['message'] = 'Site delete error' if r.deleted_count == 0 else 'site deleted'

    return result


def validator(site_data: dict) -> dict:
    result = {
        'status': False,
        'message': "Data error",
    }

    
    if 'name' not in site_data.keys() or type(site_data['name']) is not str or len(site_data['name']) < 2:
        result['message'] = f"'{str(site_data['name'])}' is not a valid site name"
        return result

    if 'script_id' not in site_data.keys() or type(site_data['script_id']) is not str or len(site_data['script_id']) != 24:
        result['message'] = f"script id is required"
        return result

    if 'server_id' not in site_data.keys() or type(site_data['server_id']) is not str or len(site_data['server_id']) != 24:
        result['message'] = f"Server id is required"
        return result

    if 'domain' not in site_data.keys() or type(site_data['domain']) is not str or len(site_data['domain']) < 4:
        result['message'] = f"Domain is required"
        return result

    # server validation
    server_data = servers.load_one({'id': site_data['server_id']})

    if type(server_data) is not dict or len(server_data) == 0:
        result['message'] = f"Server not found"
        return result

    # Domain name DNS validation
    # if not is_domain_on_server(site_data['domain'], server_data['ipv4']):
    #    result['message'] = f"Domain {site_data['domain']} is not redirected on selected server"
    #    return result

    # Domain name validation
    pre = re.compile(
        r'^(?=.{1,253}$)(?!.*\.\..*)(?!\..*)([a-zA-Z0-9-]{,63}\.){,127}[a-zA-Z0-9-]{1,63}$')
    if not pre.match(site_data['domain']):
        result['message'] = f"Domain name {site_data['domain']} is invalid"
        return result

    # Optional Dev domain name validation
    if 'dev_domain' in site_data.keys() and type(site_data['dev_domain']) is str and len(site_data['dev_domain']) > 3 and not pre.match(site_data['dev_domain']):
        result['message'] = f"Dev domain name {site_data['dev_domain']} is invalid"
        return result

    # Optional Alias domains name validation
    if 'alias_domains' in site_data.keys() and type(site_data['alias_domains']) is str and len(site_data['alias_domains']) > 3:

        for alias_domain in site_data['alias_domains'].splitlines():

            if len(alias_domain) < 4 or not pre.match(alias_domain):
                result['message'] = f"Alias domain name {alias_domain} is invalid"
                return result

    # script validation
    script_data = scripts.load_one({'id': site_data['script_id']})

    if type(script_data) is not dict or len(script_data) == 0:
        result['message'] = f"script not found"
        return result

    result['status'] = True

    return result


def is_domain_on_server(domain: str, server_ip: str) -> dict | bool:
    dns_records = utils.domain_dns_info(domain, ['A', 'CNAME', 'ALIAS'])

    if len(dns_records) > 0:

        for r in dns_records:
            if r['type'] == 'A' and r['value'] == server_ip:
                return True

            if r['type'] in ['CNAME', 'ALIAS']:
                dns_records_cn = utils.domain_dns_info(r['value'], ['A'])

                for x in dns_records_cn:
                    if x['type'] == 'A' and x['value'] == server_ip:
                        return True

    return False


def site_model(site_data: dict) -> dict:

    site = {
        'name': utils.eval_key('name', site_data),
        'description': utils.eval_key('description', site_data),
        'server_id': utils.eval_key('server_id', site_data),
        'script_id': utils.eval_key('script_id', site_data),
        'publish': utils.eval_key('publish', site_data, 'bool'),
        'home_dir': utils.eval_key('home_dir', site_data),
        'domain': utils.eval_key('domain', site_data),
        'dev_domain': utils.eval_key('dev_domain', site_data),
        'alias_domains': utils.eval_key('alias_domains', site_data, 'list'),
        'owner': utils.eval_key('owner', site_data),
        'creator': utils.eval_key('creator', site_data),
        'created_at': utils.eval_key('created_at', site_data),
        'updated_at': utils.eval_key('updated_at', site_data),
    }

    return site
