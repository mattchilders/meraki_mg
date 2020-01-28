import meraki
import requests
import json

BASE_API_URL = 'https://api.meraki.com/api/v0/'
GET_ORGS_URL = 'organizations'
GET_NETWORK_URL = '/organizations/{0}/networks'
GET_CLIENT_URL = '/networks/{0}/clients?perPage={1}&timespan={2}'


def update_uplink(api_key, network_id, serial, uplink, uplink_vlan, uplink_ip=None, uplink_mask=None, uplink_gw=None, uplink_dns1=None, uplink_dns2=None, dhcp=False):
    uplink_url = 'https://api.meraki.com/api/v0/networks/' + str(network_id) + '/devices/' + str(serial) + '/uplinkInterfaceSettings'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    if ('wan1' not in uplink and 'wan2' not in uplink):
        print('Error, invalid uplink.  Please use "wan1" or "wan2" for uplink')
        return None

    dns = []
    if uplink_dns1:
        dns.append(uplink_dns1)
    if uplink_dns2:
        dns.append(uplink_dns2)

    if dhcp:
        payload = {uplink: {"usingStaticIp": False, "vlan": uplink_vlan}}
    else:
        payload = {uplink: {"usingStaticIp": True, "staticIp": uplink_ip, "staticSubnetMask": uplink_mask, "staticGatewayIp": uplink_gw, "staticDns": dns, "vlan": uplink_vlan}}

    try:
        response = requests.request('PUT', uplink_url, headers=headers, data=json.dumps(payload), allow_redirects=True, timeout=30)
        if response.status_code != 200:
            print("Error Updating Uplink")
            print('Status Code:' + str(response.status_code))
            print('Response: ' + response.text)
            return None
        return response.status_code
    except Exception as e:
        print('Error Updating Uplink: ')
        if response:
            print('Status Code:' + str(response.status_code))
            print('Response: ' + response.text)
        print(e)
        return None


def get_api_key(config_file):
    with open(config_file, 'r') as config:
        config_settings = config.read()

    settings = json.loads(config_settings)
    api_key = settings['api_key']
    return api_key


def get_org_id(api_key, org_name):
    orgs = meraki.myorgaccess(api_key, suppressprint=True)
    for org in orgs:
        if org['name'] == org_name:
            return org['id']

    print('Error: Org Not found: ' + org_name)
    return None


def get_network(api_key, org_id, network_name):
    networks = meraki.getnetworklist(api_key, org_id, suppressprint=True)
    for network in networks:
        if network['name'] == network_name:
            return network['id']

    print('Error: Network Not found: ' + network_name)
    return None


def get_device_serial(api_key, network_id, device_name):
    devices = meraki.getnetworkdevices(api_key, network_id, suppressprint=True)
    for device in devices:
        if device['name'] == device_name:
            return device['serial']

    print('Error: Device Not found: ' + device_name)
    return None


def get_api(api_key, url, timeout=30):
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}
    response = requests.request('GET', url, headers=headers, allow_redirects=True, timeout=90)
    return response


def find_match(data, key, match):
    data = json.loads(data)
    for line in data:
        if line[key] == match:
            return line['id']
    return None, data


def get_org_id_by_name(api_key, name):
    url = BASE_API_URL + GET_ORGS_URL
    response = get_api(api_key, url)
    id = find_match(response.text, 'name', name)
    if id is None:
        print('Organization ' + name + ' not found')
    return id


def print_org_list(api_key):
    url = BASE_API_URL + GET_ORGS_URL
    response = get_api(api_key, url)
    data = json.loads(response.text)
    print('{:<20} {:40}'.format('Org Id', 'Org Name'))
    print('{:<20} {:40}'.format('-' * 15, '-' * 35))
    for line in data:
        print('{:<20} {:40}'.format(line['id'], line['name']))


def get_network_id_by_name(api_key, org_id, name):
    url = BASE_API_URL + GET_NETWORK_URL.format(org_id)
    response = get_api(api_key, url)
    id = find_match(response.text, 'name', name)
    if id is None:
        print('Network ' + name + ' not found')
    return id


def print_network_list(api_key, org_id):
    url = BASE_API_URL + GET_NETWORK_URL.format(org_id)
    response = get_api(api_key, url)
    data = json.loads(response.text)
    print('{:<30} {:40}'.format('Network Id', 'Network Name'))
    print('{:<30} {:40}'.format('-' * 15, '-' * 35))
    for line in data:
        print('{:<30} {:40}'.format(line['id'], line['name']))


def get_client_id_by_name(api_key, network_id, name):
    url = BASE_API_URL + GET_CLIENT_URL.format(network_id)
    response = get_api(api_key, url)
    id = find_match(response.text, 'description', name)
    if id is None:
        print('Network ' + name + ' not found')
    return id


def print_clients_list(api_key, network_id, pages=1000, lookback_secs=604800):
    url = BASE_API_URL + GET_CLIENT_URL.format(network_id, pages, lookback_secs)
    response = get_api(api_key, url)
    data = json.loads(response.text)
    print('{:<30} {:40}'.format('Client Id', 'Client Name'))
    print('{:<30} {:40}'.format('-' * 15, '-' * 35))
    for line in data:
        description = (line['description'] or (line['manufacturer'] + ' ' + line['os'])) or line['mac']
        print('{:<30} {:40}'.format(line['id'], description))


if __name__ == '__main__':
    main()
