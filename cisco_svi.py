#!/usr/bin/env python
# -*- coding: utf-8 -*-

from netmiko import ConnectHandler
from getpass import getpass
from ntc_templates.parse import parse_output
import json

password = getpass()
args = {'username': 'krrichar', 'password': password,
        'device_type': 'cisco_nxos'}
change = input('change or rollback: ').lower()

with open('upstream_schema.json') as f:
    json = json.load(f)


def login(device):
    """ log into each device in the json file "device"
        ave running configuration before changes
        use for prechex to gather configuration backup """
    global net_connect
    net_connect = ConnectHandler(device, session_log=device, **args)
    print(net_connect.find_prompt())
    net_connect.send_command('show run')
    output = net_connect.save_config()
    if 'startup-config' in output:
        output += net_connect.send_command_timing('\n')


def interface_cfg(device, vlan, desc, addr, standby):
    """ interface commands to create interface configuration """
    commands = [
        'interface vlan {}'.format(vlan),
        'description {}'.format(desc),
        'ip address {}'.format(addr),
        'no ip redirects',
        'no ip unreachables',
        'hsrp version 2',
        'hsrp {}'.format(vlan),
        'preempt',
        'ip {}'.format(standby)
    ]
    net_connect.send_config_set(commands)

    #  configure hsrp priority on router 1 only
    if 'vdc1' in device:
        net_connect.send_config_set([
            'interface vlan {}'.format(vlan),
            'hsrp {}'.format(vlan),
            'priority 200'])
    net_connect.send_command('clear ip arp vlan {0}'.format(vlan))
        
    #  interface configuration will be sent to stdout
    print(net_connect.send_command(
        'show run interface {}'.format(vlan)))


def bgp_cfg(network):
    """ cli output is parsed into a dictionary from returned text
        variables set for bgp configuration structure """
    bgp_sum = net_connect.send_command('show ip bgp summary')
    bgp_parsed = parse_output(platform='cisco_ios',
                              command='show ip bgp summary',
                              data=bgp_sum)
    for item in bgp_parsed:
        local = item.get('local_as')
        bgp_config = ['router bgp {}'.format(local),
                      'address-family ipv4 unicast',
                      'network {} route-map SET-CORE-COMMUNITY'.format(network)]

    #  bgp configuration for new network
    net_connect.send_config_set(bgp_config)
    
    #  bgp configuration will be sent to stdout
    print(net_connect.send_command('show run | sec bgp'))


def rollback(vlan, network):
    """ interface commands to delete interface and bgp configurations """
    commands = ['no interface vlan{}'.format(vlan)]
    net_connect.send_config_set(commands)
    #  cli output is parsed into a dictionary from returned text
    #  bgp variables set for configuration structure
    bgp_sum = net_connect.send_command('show ip bgp summary')
    bgp_parsed = parse_output(platform='cisco_ios',
                              command='show ip bgp summary',
                              data=bgp_sum)
    for item in bgp_parsed:
        local = item.get('local_as')
        bgp_config = ['router bgp {}'.format(local),
                      'address-family ipv4',
                      'no network{}'.format(network)]

    #  remove bgp configuration
    net_connect.send_config_set(bgp_config)


def disconnect(device):
    """ save running configuration
        disconnect from the device """
    output = net_connect.save_config()
    if 'startup-config' in output:
        output += net_connect.send_command_timing('\n')
    net_connect.disconnect()


def main():
    """ define variables from json dictionary to be used as global values """
    for obj in json:
        device = obj.get('device')
        vlan = obj.get('vlan')
        desc = obj.get('desc')
        network = obj.get('network')
        addr = obj.get('addr')
        standby = obj.get('standby')

        login(device)

        # change type will determine which function is called
        if change == 'change':
            interface_cfg(device, vlan, desc, addr, standby)
            bgp_cfg(network)
        elif change == 'rollback':
            rollback(vlan, network)

        disconnect(device)


if __name__ == '__main__':
    main()
