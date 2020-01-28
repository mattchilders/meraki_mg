import meraki
from meraki_helpers import *


def main():
    org_name = 'OrgName'
    cloned_network = 'cloned_network'
    new_network = 'new_netowrk'
    network_type = ' cellularGateway '

    config_file = 'config.json'
    api_key = get_api_key(config_file)
    org_id = get_org_id(api_key, org_name)

    clone_gold_network(api_key, org_id, cloned_network, new_network, network_type=network_type)


def clone_gold_network(api_key, org_id, cloned_network, new_network, tz='America/Chicago', tags=None, network_type=' switch '):
    network_id = get_network(api_key, org_id, cloned_network)
    print('Cloning network ' + cloned_network + ' (' + network_id + ') to new network ' + new_network)
    if tags is None:
        tags = ['new']
    response = meraki.addnetwork(api_key, org_id, new_network, network_type, tags, tz, cloneid=network_id, suppressprint=False)
    print(response)


if __name__ == '__main__':
    main()
