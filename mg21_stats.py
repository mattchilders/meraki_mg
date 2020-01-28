from meraki_helpers import *
import meraki


ORG_NAME = 'OrgName'
NETWORK_NAME = 'networkname'

config_file = 'config.json'
api_key = get_api_key(config_file)
org_id = get_org_id(api_key, ORG_NAME)
network_id = get_network(api_key, org_id, NETWORK_NAME)

devices = meraki.getnetworkdevices(api_key, network_id, suppressprint=True)

mg_list = []

for device in devices:
    if 'MG21' in device['model']:
        serial = device['serial']
        uplinks = meraki.getdeviceuplink(api_key, network_id, serial, suppressprint=True)
        for uplink in uplinks:
            if uplink['interface'] == 'Cellular':
                uplink_data = uplink
                del uplink_data['model']
        device.update(uplink_data)
        mg_list.append(device)


print("MGs in Network: " + NETWORK_NAME)
print('=' * 40)
for mg in mg_list:
    signal = mg['signal']
    signals = signal.split(' ')
    # signal_labels = signals[0].split(',')
    signal_values = signals[1].split(',')
    rsrp = signal_values[0]
    rsrq = signal_values[1]
    print('Name: ' + mg['name'])
    print('Model: ' + mg['model'])
    print('Serial:' + mg['serial'])
    print('Status: ' + mg['status'])
    print('IP: ' + mg['ip'])
    print('Provider: ' + mg['provider'])
    print('Type: ' + mg['connectionType'])
    print('RSRP: ' + str(rsrp))
    print('RSRQ: ' + str(rsrq))
    print('=' * 40)
    print()

print(mg_list)
