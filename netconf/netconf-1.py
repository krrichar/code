from ncclient import manager

router = {
    'name': 'ios-xe-mgmt-latest.cisco.com', 
    'port': '10000',
    'username': 'developer',
    'password': 'C1sco12345'
}

with manager.connect(host=router['name'], port=router['port'], username=router['username'], password=router['password'], hostkey_verify=False) as m:
    m.close_session()