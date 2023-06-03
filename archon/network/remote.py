import asyncio
import asyncssh
import json
import re
from slugify import slugify
from archon import app, utils
from archon.models.servers import servers, services
from archon.models.scripts import scripts
from archon.models.sites import sites
from archon.models.servers import servers
from archon.models.notifications import notifications
from archon.mailer import mailer


async def run_client(server, tasks=[], script=None, service_installer=False) -> dict:

    result = {
        'status': False,
        'message': f"Server {server['name']}: ",
        'shell': []
    }

    if 'ssh_key' in server.keys() and len(server['ssh_key']) > 0:
        result['auth_method'] = 'Private key'

        try:
            async with asyncssh.connect(server['ipv4'], port=int(server['ssh_port']), username=server['ssh_user'], client_keys=[server['ssh_key']], known_hosts=None) as conn:
                result = await run_task(conn, tasks, script, service_installer, result)

        except(asyncssh.Error) as exc:
            result['message'] = f"Server {server['name']}: {str(exc)}"
    else:
        result['auth_method'] = 'Password'

        try:
            async with asyncssh.connect(server['ipv4'], port=int(server['ssh_port']), username=server['ssh_user'], password=server['ssh_pwd'], known_hosts=None) as conn:
                #print(script)
                result = await run_task(conn, tasks, script, service_installer, result)

        except(asyncssh.Error) as exc:
            result['message'] = f"Server {server['name']}: {str(exc)}"

    return result


async def run_task(conn, tasks, script, service_installer, result) -> dict:

    if type(script) is dict:
        result = await process_script_file(conn, script, result)

    if service_installer == True:
        result = await process_service_files(conn, result)

    for task in tasks:
        response = await conn.run(task, check=False)
        result['shell'].append(response.stdout)

    conn.close()
    result['message'] += f"Task completed"
    result['status'] = True

    return result


async def process_script_file(conn, script, result) -> dict:
    cache_dir = app.config['filesystem']['scripts']
    cache_file = slugify(f"{utils.now()}-{script['name']}") + ".sh"

    # Check remote dir for scripts
    response = await conn.run(as_root('mkdir -p /opt/archon/scripts'), check=False)
    result['shell'].append(response.stdout)
    response = await conn.run(as_root('chown $(ls - ld ~ | awk \'{print $3}\') /opt/archon/scripts'), check=False)
    result['shell'].append(response.stdout)

    # Cache script file localy
    utils.file_save(f"{cache_dir}/{cache_file}",
                    utils.dos2unix(script['content']))

    # Transfer script file
    # Returns None type, so we can't log
    await asyncssh.scp(f"{cache_dir}/{cache_file}", (conn, f"/opt/archon/scripts/{cache_file}"))

    # Make script file executable
    response = await conn.run(as_root(f"chmod +x /opt/archon/scripts/{cache_file}"), check=False)
    result['shell'].append(response.stdout)

    # Run script in remote dir
    script['arguments'] = domain_unique(script['arguments'])
    response = await conn.run(as_root(f"/opt/archon/scripts/{cache_file} {compose_script_call_args(script['arguments'])}"), check=False)
    result['shell'].append(response.stdout)

    return result


def deploy(site_id) -> dict:
    site = sites.load_one({
        'id': site_id
    })

    # Site validation
    if type(site) is not dict:
        return {
            'status': False,
            'message': f"Invalid site",
            'shell': []
        }

    server = servers.load_one({
        'id': site['server_id']
    })

    script = scripts.load_one({
        'id': site['script_id']
    })

    # script validation
    if type(script) is not dict or 'content' not in script or script['safe'] == False:
        return {
            'status': False,
            'message': f"Invalid or unsafe script",
            'shell': []
        }

    # Domain name validation
    if type(server) is not dict or 'ipv4' not in server:
        return {
            'status': False,
            'message': f"Domain {site['domain']} is not redirected on selected server",
            'shell': []
        }

    tasks = []

    script['arguments'] = {
        'home_dir': site['home_dir'],
        'domain': '',
        'dev_domain': '',
        'alias_domains': []
    }

    valid_domains = []

    # Validate domain DNS entries
    if sites.is_domain_on_server(site['domain'], server['ipv4']) == True:
        valid_domains.append(site['domain'])
        script['arguments']['domain'] = site['domain']


    # Validate dev_domain DNS entries
    if 'dev_domain' in site.keys() and type(site['dev_domain']) is str and len(site['dev_domain']) > 3 and sites.is_domain_on_server(site['dev_domain'], server['ipv4']) == True:
        valid_domains.append(site['dev_domain'])
        script['arguments']['dev_domain'] = site['dev_domain']

    # Validate alias domains DNS entries
    if 'alias_domains' in site.keys() and type(site['alias_domains']) is list and len(site['alias_domains']) > 0:

        for alias_domain in site['alias_domains']:

            if sites.is_domain_on_server(alias_domain, server['ipv4']) == True:
                valid_domains.append(alias_domain)
                script['arguments']['alias_domains'].append(alias_domain)

    if len(valid_domains) == 0:
        return {
            'status': False,
            'message': f"None of the specified domains are redirected to the selected server",
            'shell': []
        }

    script['valid_domains'] = valid_domains

    result = init_client(server, tasks, script)

    # Notify and parse shell response
    parsed = parse_shell_result("\n".join(result['shell']))
    notifications.email('settings.notifications.sites',
                        parsed['template'], f"{app.config['name']} - site deployed", parsed['html_message_data'], parsed['result'])
    notifications.db(
        'site', site_id, f"Site {site['name']} deployed.", parsed['nice'])

    result['shell'] = [parsed['nice']]

    return result


def parse_shell_result(result) -> dict:
    tag_result = result

    custom_tag = utils.tag_parse('control-result', result)

    if len(custom_tag) > 0:
        tag_result = custom_tag

    html_message_data = {
        'app_full_name': app.config['full_name'],
    }
    try:
        json_object = json.loads(tag_result)
        html_message_data['data'] = json.dumps(json_object, indent=4)
        template = 'deploy-json'

    except ValueError as e:
        html_message_data['data'] = tag_result
        template = 'deploy-text'

    return {
        'result': result,
        'nice': html_message_data['data'],
        'template': template,
        'html_message_data': html_message_data
    }


def test_connection(server_id) -> dict:
    server = servers.load_one({
        'id': server_id
    })

    if type(server) is not dict or 'ipv4' not in server:
        return {
            'status': False,
            'message': f"Server {server_id} not found",
            'shell': []
        }

    tasks = [
        'echo "SSH server hostname: $(hostname)"',
        'echo "$(uname -a)"',
        'echo "$(cat /etc/os-release)"',
        as_root('mkdir -p /opt/archon/scripts'),
        'echo "Monitoring service is $(systemctl is-active archon-monitor-collector.service)"',
    ]

    return init_client(server, tasks)


async def process_service_files(conn, result) -> dict:
    cache_dir = app.config['filesystem']['scripts']
    config_cache_file = "archon-monitor-install.sh"
    script_cache_file = "archon-monitor.sh"

    # Check remote dir for scripts
    response = await conn.run(as_root('mkdir -p /opt/archon/scripts'), check=False)
    result['shell'].append(response.stdout)
    response = await conn.run(as_root('mkdir -p /opt/archon/monitor'), check=False)
    result['shell'].append(response.stdout)

    response = await conn.run(as_root('chown $(ls -ld ~ | awk \'{print $3}\') /opt/archon/scripts'), check=False)
    result['shell'].append(response.stdout)
    response = await conn.run(as_root('chown $(ls -ld ~ | awk \'{print $3}\') /opt/archon/monitor'), check=False)
    result['shell'].append(response.stdout)

    # Cache files localy
    utils.file_save(f"{cache_dir}/{config_cache_file}",
                    utils.dos2unix(services.monitor_service_config()))
    utils.file_save(f"{cache_dir}/{script_cache_file}",
                    utils.dos2unix(services.monitor_service_script()))

    # Transfer script filess
    # Returns None type, so we can't log
    await asyncssh.scp(f"{cache_dir}/{config_cache_file}", (conn, f"/opt/archon/scripts/{config_cache_file}"))
    await asyncssh.scp(f"{cache_dir}/{script_cache_file}", (conn, f"/opt/archon/monitor/{script_cache_file}"))

    response = await conn.run(as_root(f"dos2unix /opt/archon/scripts/{config_cache_file}"), check=False)
    result['shell'].append(response.stdout)
    response = await conn.run(as_root(f"dos2unix /opt/archon/monitor/{script_cache_file}"), check = False)
    result['shell'].append(response.stdout)

    # Make script file executable
    response = await conn.run(as_root(f"chmod +x /opt/archon/scripts/{config_cache_file}"), check=False)
    result['shell'].append(response.stdout)
    response = await conn.run(as_root(f"chmod +x /opt/archon/monitor/{script_cache_file}"), check = False)
    result['shell'].append(response.stdout)

    # Run install script in remote dir
    response = await conn.run(as_root(f"/opt/archon/scripts/{config_cache_file}"), check=False)
    result['shell'].append(response.stdout)

    return result


def domain_unique(script_arguments) -> dict:
    new_aliases = []
    if len(script_arguments['dev_domain']) > 0 and script_arguments['domain'] == script_arguments['dev_domain']:
       script_arguments['dev_domain'] = ''

    if type(script_arguments['alias_domains']) is list and len(script_arguments['alias_domains']) > 0:

        for alias_domain in script_arguments['alias_domains']:
            if alias_domain != script_arguments['domain'] and alias_domain != script_arguments['dev_domain'] and alias_domain not in new_aliases:
                new_aliases.append(alias_domain)

    script_arguments['alias_domains'] = new_aliases
    return script_arguments


def compose_script_call_args(script_arguments) -> str:
    cmd = f""

    if len(script_arguments['home_dir']) > 0:
        cmd += f" --home_dir {script_arguments['home_dir']}"

    if len(script_arguments['domain']) > 0:
        cmd += f" --domain {script_arguments['domain']}"

    if len(script_arguments['dev_domain']) > 0:
        cmd += f" --dev_domain {script_arguments['dev_domain']}"

    if type(script_arguments['alias_domains']) is list and len(script_arguments['alias_domains']) > 0:
        cmd += f" --alias_domains {':'.join(script_arguments['alias_domains'])}"

    return cmd


def install_monitoring_service(server_id) -> dict:
    server = servers.load_one({
        'id': server_id
    })

    tasks = [
        'echo "SSH server hostname: $(hostname)"',
        'echo "Monitoring service is $(systemctl is-active archon-monitor-collector.service)"'
    ]

    return init_client(server=server, tasks=tasks, script=None, service_installer=True)


def validate_dns_entry(domain, server_ipv4) -> bool:
    if not sites.is_domain_on_server(domain, server_ipv4):
        return False
    return True


def detect_root(server_id) -> dict:
    server = servers.load_one({
        'id': server_id
    })

    if type(server) is not dict or 'ipv4' not in server:
        return {
            'status': False,
            'message': f"Server {server_id} not found",
            'shell': []
        }

    tasks = [
        f"if [[ $EUID == 0 ]];then AR=\"root\"; elif [[ $(which sudo) ]] && [[ $EUID != 0 ]];then AR=\"sudo\"; else AR=\"none\"; fi; echo -n $AR",
    ]

    return init_client(server, tasks)


def as_root(command) -> str:
    pattern = f"if [[ $EUID == 0 ]];then {command}; elif [[ $(which sudo) ]] && [[ $EUID != 0 ]];then sudo {command}; else echo \"No root condition, can't run on this machine\"; fi;"
    return pattern


def init_client(server, tasks, script=None, service_installer=False) -> dict:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    r = asyncio.get_event_loop().run_until_complete(
        run_client(server, tasks, script, service_installer))
    return r
