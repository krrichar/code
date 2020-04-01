#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from getpass import getpass
from netmiko import ConnectHandler
from ntc_templates.parse import parse_output


password = getpass()
args = {'username': 'krrichar', 'password': password,
        'device_type': 'cisco_nxos'}
change = input('change or rollback: ').lower()

with open('sp_schema.json') as f:
    json = json.load(f)


def login(device):
    """
    log into each device in the json file "device"
    ave running configuration before changes
    use for prechex to gather configuration backup
    """
    global net_connect
    net_connect = ConnectHandler(device, session_log=device, **args)
    print(net_connect.find_prompt())
    net_connect.send_command('show run')
    output = net_connect.save_config()
    if 'startup-config' in output:
        output += net_connect.send_command_timing('\n')


def route_cfg(net, next_hop):
    """
    create static route for sure payroll in dmz
    """
    commands = ['ip route {} {}'.format(net, next_hop)]
    net_connect.send_config_set(commands)
    print(net_connect.send_command(r'show run | grep "ip route"'))


def bgp_cfg(net):
    """
    cli output is parsed into a dictionary from returned text
    variables set for bgp configuration structure
    """
    bgp_sum = net_connect.send_command('show ip bgp summary')
    bgp_parsed = parse_output(platform='cisco_ios',
                              command='show ip bgp summary',
                              data=bgp_sum)
    for item in bgp_parsed:
        local = item.get('local_as')
        bgp_config = ['router bgp {}'.format(local),
                      'address-family ipv4 unicast',
                      'network {} route-map SET-CORE-COMMUNITY'.format(net)]
    net_connect.send_config_set(bgp_config)
    print(net_connect.send_command('show run | sec bgp'))


def rollback(net):
    """
    interface commands to delete interface and bgp configurations
    """
    commands = ['no ip route {}'.format(net)]
    net_connect.send_config_set(commands)
    bgp_sum = net_connect.send_command('show ip bgp summary')
    bgp_parsed = parse_output(platform='cisco_ios',
                              command='show ip bgp summary',
                              data=bgp_sum)
    for item in bgp_parsed:
        local = item.get('local_as')
        bgp_config = ['router bgp {}'.format(local),
                      'address-family ipv4',
                      'no network{}'.format(net)]
    net_connect.send_config_set(bgp_config)


def disconnect():
    """
    save running configuration
    disconnect from the device
    """
    output = net_connect.save_config()
    if 'startup-config' in output:
        output += net_connect.send_command_timing('\n')
    net_connect.disconnect()


def main():
    """
    define variables from json dictionary to be used as global values
    """
    for obj in json:
        device = obj.get('device')
        net = obj.get('route')
        next_hop = obj.get('next_hop')
        login(device)
        if change == 'change':
            route_cfg(net, next_hop)
            bgp_cfg(net)
        elif change == 'rollback':
            rollback(net)
        disconnect()


if __name__ == '__main__':
    main()
