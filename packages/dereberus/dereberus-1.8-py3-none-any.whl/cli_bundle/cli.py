from pathlib import Path
import click
from tabulate import tabulate
from cli_bundle.dereberus import DereberusApi, get_credentials
import json, os

@click.group()
def dereberus_commands():
    pass

  
def change_realm(realm):
  try:
    with open(f'{Path.home()}/.dereberus/user_credentials.json',"r") as file:
        data = json.load(file)
    data["realm"] = realm
    with open(f'{Path.home()}/.dereberus/user_credentials.json', "w") as file:
        json.dump(data, file, indent=4)   
  except (FileNotFoundError, json.JSONDecodeError): 
      return

def read_public_key(public_key_path):
    full_path = os.path.expanduser(public_key_path)
    with open(full_path, 'r') as openfile:
        public_key = openfile.read()
    return public_key

def get_valid_resource(resource=None, service=None, client=None):
    try:
        while True:
            if not resource and not service:
                user_input = click.prompt('Enter Resource or service (format: client|service)')
                if "|" in user_input:
                    client,service = user_input.split("|", 1)
                else:
                    resource = user_input
            if service and not client:
                client = click.prompt('Enter the Client name for the service')
            if client and not service:
                client = click.prompt('Enter the Service name for the client')
            if service and client:
                data = {"service_name": service, "client_name": client}
                endpoint = '/requests/validate_service'
            else:
                data = {"resource_name": resource}
                endpoint = '/requests/resources'
            valid_response = DereberusApi.post(get_credentials('DEREBERUS_TOKEN'), endpoint, data=data)

            if valid_response.status_code == 200:
                if endpoint == '/requests/validate_service':
                    resource = valid_response.json()['resource']
                return resource
            click.echo("Invalid input. Please try again.")
            resource, service, client = None, None, None
    except Exception as e:
        click.echo(f"Error in job execution: {e}")
        return


@dereberus_commands.command()
@click.argument('realm',required=False) 
def login(realm):
    realm = 'qa' if realm is None else change_realm(realm)
    # Assuming the user has already logged in and has an API token written in the user_credentials.json file
    user_api_token = get_credentials('user_api_token')
    if user_api_token is None: # the API token is not present in the file
        click.echo('API token not found')
        return
    # check the API token is valid or not
    user_data = DereberusApi.post(get_credentials('DEREBERUS_TOKEN'), '/auth/login', data={'user_api_token': user_api_token})
    if user_data.status_code != 200:
        click.echo(user_data.json()['message'])
        return
    click.echo(user_data.json()['message'])
    # check if the public key is already set up
    if user_data.json().get('key_exist') == False: 
        public_key_path = click.prompt('Enter the path to your public key file')
        public_key = read_public_key(public_key_path)
        response = DereberusApi.post(get_credentials('DEREBERUS_TOKEN'), '/auth/setup_public_key', data={'public_key': public_key, 'user_api_token': user_api_token})
        if response.status_code != 200:
            click.echo(response.json().get('message'))
            return
        click.echo(response.json().get('message'))
        request_callback()
        return  
    click.echo("Public key is already set up.")
    click.echo("Do you want to change it? (y/n)")
    choice = input()
    if choice.lower() == 'n':
        request_callback()
        return
    public_key_path = click.prompt('Enter the path to your public key file')
    public_key = read_public_key(public_key_path)
    response = DereberusApi.post(get_credentials('DEREBERUS_TOKEN'), '/auth/setup_public_key', data={'public_key': public_key, 'user_api_token': user_api_token})
    if response.status_code != 200:
        click.echo(response.json().get('message'))
        return
    click.echo(response.json().get('message'))
    request_callback()
    return

@dereberus_commands.command()
@click.argument('realm', required=False)
@click.option('--resource', '-r', required=False, help="Resource name to request")
@click.option('--service', '-s', required=False, help="service name to request")
@click.option('--client', '-c', required=False, help="Client name for the service")
@click.option('--reason', '-m', required=False, help="Reason for requesting access")
def request(realm, resource, service, client, reason):
    realm = 'qa' if realm is None else change_realm(realm)
    if service and not client:
        click.echo("Error: If you specify a service, you must also provide a client using -c")
        return
    if not service and client:
        click.echo("Error: If you specify a client, you must also provide a service using -s")
        return
    resource = get_valid_resource(resource, service, client)
    if not resource and not service:
        click.echo("Invalid input. Please enter a valid resource or service|client.")
        return
    if not reason:
        reason = click.prompt('Enter the Reason')
    process_request(resource, reason)

def process_request(resource,reason):
  user_api_token = get_credentials('user_api_token')
  if user_api_token is None:
    click.echo('API token not found')
    return
#   click.echo("resource:",resource)
  resource_response = DereberusApi.post(get_credentials('DEREBERUS_TOKEN'), '/requests/create', data={"resource_name": resource, "reason": reason, "user_api_token": user_api_token})
  if resource_response.status_code != 200:
    click.echo(resource_response.json().get('message'))
    return
  click.echo(resource_response.json().get('message'))
  return
  
def request_callback():
    resource = get_valid_resource()
    reason = click.prompt('Enter the Reason')
    process_request(resource, reason)
    return

@dereberus_commands.command()
@click.argument('realm',required=False) 
def resource(realm):
    realm = 'qa' if realm is None else change_realm(realm)
    user_api_token = get_credentials('user_api_token')
    if user_api_token is None:
        click.echo('API token not found')
        return
    list_response = DereberusApi.get(get_credentials('DEREBERUS_TOKEN'), '/resources/list', data={'user_api_token': user_api_token})
    if list_response.status_code != 200:
      click.echo(list_response.json().get('message'))
      return
    resources = list_response.json()
    headers = ["name", "ip"]
    rows = [[req.get(header, "") for header in headers] for req in resources]
    click.echo(tabulate(rows, headers=headers, tablefmt="psql"))

@dereberus_commands.command()
@click.argument('realm',required=False) 
@click.option('--mode', type=click.Choice(['pending', 'approved', 'all'], case_sensitive=False), default='pending', help='Filter requests by status.')
def list(realm,mode):
    realm = 'qa' if realm is None else change_realm(realm)
    user_api_token = get_credentials('user_api_token')
    if user_api_token is None:
        click.echo('API token not found')
        return
    list_response = DereberusApi.post(get_credentials('DEREBERUS_TOKEN'), '/admin/list', data={'mode': mode, 'user_api_token': user_api_token})
    if list_response.status_code != 200:
        try:
            click.echo(list_response.json().get('message'))
        except ValueError:
            click.echo('Failed to decode JSON response')
        return
    requests = list_response.json()
    headers = ["id","mobile", "email", "ip", "reason", "status", "approver"]
    rows = [[req.get(header, "") for header in headers] for req in requests]
    click.echo(tabulate(rows, headers=headers, tablefmt="psql"))

@dereberus_commands.command()
@click.argument('realm',required=False) 
@click.option('--request-id', prompt='Enter request ID', help='ID of the request to approve')
def approve(realm,request_id):
    realm = 'qa' if realm is None else change_realm(realm)
    user_api_token = get_credentials('user_api_token')
    if user_api_token is None:
        click.echo('API token not found')
        return
    response = DereberusApi.post(get_credentials('DEREBERUS_TOKEN'), '/admin/approve', data={'request_id': request_id, 'user_api_token': user_api_token})
    if response.status_code != 200:
        try:
            click.echo(response.json().get('message'))
        except ValueError:
            click.echo('Failed to decode JSON response')
        return
    click.echo(response.json().get('message'))

@dereberus_commands.command()
@click.argument('realm',required=False) 
@click.option('--request-id', prompt='Enter request ID', help='ID of the request to reject')
def reject(realm,request_id):
    realm = 'qa' if realm is None else change_realm(realm)
    user_api_token = get_credentials('user_api_token')
    if user_api_token is None:
        click.echo('API token not found')
        return
    response = DereberusApi.post(get_credentials('DEREBERUS_TOKEN'), '/admin/reject', data={'request_id': request_id, 'user_api_token': user_api_token})
    if response.status_code != 200:
        try:
            click.echo(response.json().get('message'))
        except ValueError:
            click.echo('Failed to decode JSON response')
        return
    click.echo(response.json().get('message'))

dereberus_commands.add_command(login)
dereberus_commands.add_command(request)
dereberus_commands.add_command(list)
dereberus_commands.add_command(approve)
dereberus_commands.add_command(reject)
dereberus_commands.add_command(resource)

if __name__ == '__main__':
    dereberus_commands()