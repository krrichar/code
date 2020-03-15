#!/bin/env python
"""
This script creates a full LTM configuration endpoint including
nodes, pool and virtual server.
"""

from getpass import getpass
from f5.bigip import ManagementRoot

USER = 'admin'
PASSWORD = getpass()
HOST = '192.168.10.5'
MGMT = ManagementRoot(HOST, USER, PASSWORD)
LTM = MGMT.tm.ltm


def create_node(partition, name):
    """
    Create LTM node.
    """
    for node in name:
        global nodes
        nodes = []
        LTM.nodes.node.create(partition=partition, name=node, address=None)
        nodes.append(node)
        

def create_pool(name):
    """
    Create pool and return for later use.
    """
    global pool
    pool = LTM.pools.pool.create(name=name)


def create_member(name, port, partition):
    """
    Create pool member(s).
    """
    pool_load = LTM.pools.pool.load(name=pool)
    for node in nodes:
        pool_load.members_s.members.create(partition=partition, name=node + ":" + port)


def create_virtual(profiles, name, dest, port):
    """
    Create virtual server.
    """
    vs_name = name
    profiles = [
        {
            'name': 'f5-tcp-wan',
            'context': 'clientside'
        },
        {
            'name': 'f5-tcp-lan',
            'context': 'serverside'
        },
        {
            'name': 'http-profile-default'
        }
    ]
    params = {
        'name': vs_name,
        'destination': '{}:{}'.format(dest, str(port)),
        'mask': '255.255.255.255',
        'description': 'Created by Python',
        'pool': pool,
        'profiles': profiles,
        'partition': 'Common',
        'sourceAddressTranslation':
            {
                'type': 'automap'
            },
        'vlansEnabled': True,
        'vlans': ['/Common/internal']
    }
    LTM.virtuals.virtual.create(**params)


def main():
    """
    Main program logic.
    """
    create_node(partition='partition', name=[{'name': 'n1', 'address': '1.1.1.1'},{'name': 'n2', 'address': '1.1.1.1'}])
    create_pool(name='test_pool')
    create_member(name=['m1', 'm2'], port='80', partition='Common')
    create_virtual(profiles='profiles', name='vs_test', dest='2.2.2.2', port='443')

if __name__ == '__main__':
    main()
