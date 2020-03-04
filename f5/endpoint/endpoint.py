#!/usr/bin/python
# -*- coding: utf-8 -*-

from getpass import getpass
from f5.bigip import ManagementRoot
import requests
import yaml

hosts = ['us6645ny-nelab-ltm1']
password = getpass()
requests.packages.urllib3.disable_warnings()

for host in hosts:
    mgmt = ManagementRoot(host, 'admin', password)
    ltm = mgmt.tm.ltm

    with open('endpoint.yml') as f:
        endpoints = yaml.safe_load(f)
        nodes = endpoints['nodes']
        pools = endpoints['pools']
        virtuals = endpoints['virtual servers']
        profiles = endpoints['profiles']

    #  create LTM pools and add pool members
    for node in nodes:
        ltm.nodes.node.create(partition='Common', name=node['name'], address=node['address'])

    for pool in pools:
        ltm.pools.pool.create(name=pool['name'], monitor=pool['monitor'], loadBalancingMode=pool['method'])
        load = ltm.pools.pool.load(name=pool['name'])
        for node in nodes:
            load.members_s.members.create(partition='Common', name=node['member'])

    for virtual in virtuals:
        params = {
            'name': virtual['name'],
            'destination': virtual['destination'],
            'mask': '255.255.255.255',
            'pool': virtual['pool'],
            'profiles': profiles,
            'partition': 'Common',
            'sourceAddressTranslation': {'type': 'automap'},
        }
        ltm.virtuals.virtual.create(**params)
