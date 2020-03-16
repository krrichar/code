from ncclient import manager
from pprint import pprint
import xml.dom.minidom
import xmltodict

# route list can be called from a remote file source as is:
# from <python_file_name> import router

router = {
    'name': 'ios-xe-mgmt-latest.cisco.com', 
    'port': '10000',
    'username': 'developer',
    'password': 'C1sco12345'
}

# netconf content can be read as is and used with the when open(<xml_file>)
netconf_filter = """
    <filter>
        <interfaces xmlns='urn:ietf:params:xml:ns:yang:ietf-interfaces'>
            <interface>
                <name>GigabitEthernet1</name>
            </interface>
        </interfaces>
        <interfaces-state xmlns='urn:ietf:params:xml:ns:yang:ietf-interfaces'>
            <interface>
                <name>GigabitEthernet1</name>
            </interface>
        </interfaces-state>
    </filter>
    """

with manager.connect(host=router['name'], port=router['port'], username=router['username'], password=router['password'], hostkey_verify=False) as m:
    for capability in m.server_capabilities:
        print('*' * 50)
        print(capability)
    # get the running config on the filtered out interface
    print('Connected')
    interface_netconf = m.get(netconf_filter)
    print('getting running config')
    
    # xmlDom = xml.dom.minidom.parseString(str(interface_netconf))
    # print(xmlDom.toprettyxml(indent='  '))
    # print('*' + 'Break' + '*' * 50)

    # turn xml object into a python dictionary
    interface_python = xmltodict.parse(interface_netconf.xml)[
        'rpc-reply']['data']
    pprint(interface_python)
    name = interface_python['interfaces']['interface']['name']['#text']
    print(name)

    config = interface_python['interfaces']['interface']
    op_state = interface_python['interfaces-state']['interface']

    print('Start')
    print(f'Name: {config["name"]["#text"]}')
    print(f'Description: {config["description"]}')
    print(f'Packets In: {op_state["statistics"]["in-unicast-pkts"]}')