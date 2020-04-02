#!/usr/bin/env python
# -*- coding: utf-8 -*-

from getpass import getpass
import requests
import urllib3

PASSWORD = getpass()
HOSTS = [
    'us6647ny-ppcore-ltm-n2a',
    'us6647ny-ppcore-ltm-n',
    'us6647ny-ppcore-ltm-perf',
    'us6645ny-ppcore-ltm-n2a',
    'us6645ny-ppcore-ltm-n',
    'us6645ny-ppcore-ltm-perf'
]

for host in HOSTS:
    urllib3.disable_warnings()
    url = f'https://{host}/mgmt/tm/ltm/profile/tcp'
    payload = \
        {
            "name": "tcplanoptimizedclientpf-alb-parent-custom-1800",
            "description": "idle timeout 1800",
            "defaultsFrom": "tcplanoptimizedclientpf-alb-parent",
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
