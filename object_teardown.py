#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This script takes input from the user and performs HTTPS methods
for LTM objects.  The schema file must be in json format containing
virtuals, pools and monitors (whichever type is needed).

Script should be run as:

./ file.py <hostname> <schema_file> <function>

functions include get_pool, get_monitor, get_virtual, delete_pool, 
delete_monitor, delete_virtual
"""
import json
import requests
import sys
import urllib3

HOST = sys.argv[1]
SCHEMA_FILE = sys.argv[2]
HEADERS = {'Content-Type': 'application/json',
           'Authorization': 'Basic YWRtaW46d2wzMTQ4Njg='}

urllib3.disable_warnings()

with open(SCHEMA_FILE) as v:
    DATA = json.load(v)
    VIRTUALS = DATA.get('virtuals')
    POOLS = DATA.get('pools')
    MONITORS = DATA.get('monitors')
    PAYLOAD = DATA.get('payload')


def get_monitor():
    for monitor in MONITORS:
        uri = 'https://{}/mgmt/tm/ltm/monitor/{}'.format(HOST, monitor)
        response = requests.request("GET", uri, headers=HEADERS,
                                    data=PAYLOAD, verify=False)
        byte_str = response.text.encode('utf8')
        json_dict = json.loads(byte_str)
        print(json_dict, '\n')


def delete_monitor():
    for monitor in MONITORS:
        uri = 'https://{}/mgmt/tm/ltm/monitor/{}'.format(HOST, monitor)
        response = requests.request("DELETE", uri, headers=HEADERS,
                                    data=PAYLOAD, verify=False)
        print(uri, response)


def get_pool():
    for pool in POOLS:
        uri = 'https://{}/mgmt/tm/ltm/pool/{}'.format(HOST, pool)
        response = requests.request("GET", uri, headers=HEADERS,
                                    data=PAYLOAD, verify=False)
        byte_str = response.text.encode('utf8')
        json_dict = json.loads(byte_str)
        print(json_dict.get('name'), '\n')


def delete_pool():
    for pool in POOLS:
        uri = 'https://{}/mgmt/tm/ltm/pool/{}'.format(HOST, pool)
        response = requests.request("DELETE", uri, headers=HEADERS,
                                    data=PAYLOAD, verify=False)
        print(uri, response)


def get_virtual():
    for virtual in VIRTUALS:
        uri = 'https://{}/mgmt/tm/ltm/virtual/{}'.format(HOST, virtual)
        response = requests.request("GET", uri, headers=HEADERS,
                                    data=PAYLOAD, verify=False)
        byte_str = response.text.encode('utf8')
        json_dict = json.loads(byte_str)
        print(json_dict['name']) 
        print(json_dict['pool'], '\n')


def delete_virtual():
    for virtual in VIRTUALS:
        uri = 'https://{}/mgmt/tm/ltm/virtual/{}'.format(HOST, virtual)
        response = requests.request("DELETE", uri, headers=HEADERS,
                                    data=PAYLOAD, verify=False)
        print(uri, response)


def main():
    function = eval(sys.argv[3] + '()')


if __name__ == '__main__':
    main()
