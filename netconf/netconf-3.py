from ncclient import manager
import xml.dom.minidom

router = {
    'name': 'ios-xe-mgmt-latest.cisco.com', 
    'port': '10000',
    'username': 'developer',
    'password': 'C1sco12345'
}

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

        # get method
        # passing in the schema you want to get
        interface_netconf = m.get(netconf_filter)
        xmlDom = xml.dom.minidom.parseString(str(interface_netconf))
        print(xmlDom.toprettyxml(indent='  '))
        print('*' + 'Break' + '*' * 50)