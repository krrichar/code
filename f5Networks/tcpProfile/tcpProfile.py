#!/usr/bin/env python
# -*- coding: utf-8 -*-

from getpass import getpass
import requests
import urllib3

PASSWORD = getpass()
HOSTS = [
    'us-site-a',
    'us-site-b'
]

for host in HOSTS:
    urllib3.disable_warnings()
    url = f'https://{host}/mgmt/tm/ltm/profile/tcp'
    payload = \
        {
            "name": "tcplanoptimizedclientpf",
            "description": "idle timeout 1800",
            "defaultsFrom": "tcp-lan-optimized",
            "idleTimeout": 1800,
            "keepAliveInterval": 3600
        }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
        url,
        headers={'Content-Type': 'application/json'},
        auth=('admin', PASSWORD),
        data=json.dumps(payload),
        verify=False
    )
    print(f'\n{host}:'.upper(), 'Code:', response.status_code)
    print(response.text.encode('utf8'))
