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

with open('jenkins_prod.json') as f:
    json = json.load(f)


def login(device):
    """log into each device in the json file "device"
    and save running configuration before changes
    use for prechex to gather configuration backup"""
    global net_connect
    net_connect = ConnectHandler(device, session_log=device, **args)
    print(net_connect.find_prompt())
    net_connect.send_command('show run')
    output = net_connect.save_config()
    if 'startup-config' in output:
        output += net_connect.send_command_timing('\n')


def vlan_cfg(vlan, desc):
    """interface commands to create interface configuration"""
    commands = [
        'vlan {}'.format(vlan),
        'name {}'.format(desc),
    ]
    net_connect.send_config_set(commands)
    net_connect.send_command('show vlan id {}'.format(vlan))
        

def svi_cfg(device, vlan, desc, addr, standby):
    """interface commands to create interface configuration"""
    commands = [
        'interface vlan {}'.format(vlan),
        'description [MON][DATA]{}'.format(desc),
        'ip address {}'.format(addr),
        'no ip redirects',
        'no ip unreachables',
        'hsrp version 2',
        'hsrp {}'.format(vlan),
        'preempt',
        'ip {}'.format(standby),
        'ip flow monitor NetflowMonitor input sampler NetflowSampler',
        'no ip redirects',
        'no ip ospf interface',
        'ip dhcp relay address 10.25.12.248',
        'ip dhcp relay address 10.25.16.180',
        'ip dhcp relay address 10.80.4.218',
        'ip dhcp relay address 10.45.11.91',
        'ip dhcp relay address 10.45.11.90',
        'ip dhcp relay address 10.80.6.78',
    ]
    net_connect.send_config_set(commands)
    if 'vdc1' in device:
        net_connect.send_config_set([
            'interface vlan {}'.format(vlan),
            'hsrp {}'.format(vlan),
            'priority 200'])
    print(net_connect.send_command(
        'show run interface {}'.format(vlan)))


def bgp_cfg(network):
    """cli output is parsed into a dictionary from returned text
    variables set for bgp configuration structure"""
    bgp_sum = net_connect.send_command('show ip bgp summary')
    bgp_parsed = parse_output(platform='cisco_ios',
                              command='show ip bgp summary',
                              data=bgp_sum)
    for item in bgp_parsed:
        local = item.get('local_as')
        bgp_config = ['router bgp {}'.format(local),
                      'address-family ipv4 unicast',
                      'network {} route-map SET-CORE-COMMUNITY'.format(network)]
    net_connect.send_config_set(bgp_config)    
    print(net_connect.send_command('show run | sec bgp'))


def rollback(vlan, network):
    """interface commands to delete and bgp configurations"""
    commands = ['no interface vlan{}'.format(vlan), "no vlan {}".format(vlan)]
    net_connect.send_config_set(commands)
    bgp_sum = net_connect.send_command('show ip bgp summary')
    bgp_parsed = parse_output(platform='cisco_ios',
                              command='show ip bgp summary',
                              data=bgp_sum)
    for item in bgp_parsed:
        local = item.get('local_as')
        bgp_config = ['router bgp {}'.format(local),
                      'address-family ipv4',
                      'no network{}'.format(network)]
    net_connect.send_config_set(bgp_config)


def disconnect(device):
    """save running configuration and disconnect from the device"""
    output = net_connect.save_config()
    if 'startup-config' in output:
        output += net_connect.send_command_timing('\n')
    net_connect.disconnect()


def main():
    """define variables from json dictionary to be used as global values"""
    for obj in json:
        device = obj.get('device')
        vlan = obj.get('vlan')
        desc = obj.get('desc')
        network = obj.get('network')
        addr = obj.get('addr')
        standby = obj.get('standby')
        login(device)
        if change == 'change':
            vlan_cfg(vlan, desc)
            svi_cfg(device, vlan, desc, addr, standby)
            bgp_cfg(network)
        elif change == 'rollback':
            rollback(vlan, network)
        disconnect(device)


if __name__ == '__main__':
    main()
