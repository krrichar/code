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

with open('commands.json') as f:
    hosts = json.load(f)


def main():

    #  connect handler to log into each device in the devices list
    #  use for prechex to gather configuration backup
    for host in hosts.values():
        for device in host:
            net_connect = ConnectHandler(device.get('device'), session_log=device.get('device'), **args)
            print(net_connect.find_prompt())
            net_connect.send_command('show run')
            output = net_connect.save_config()
            if 'startup-config' in output:
                output += net_connect.send_command_timing('\n')

            #  variables to be used for interface command structure
            network = device.get('network')
            address = device.get('addr')
            desc = device.get('desc')
            standby = device.get('standby')
            vlan = device.get('vlan')

            if change == 'change':

                #  interface commands to create sub-interface and upstream configurations
                commands = [
                    'interface vlan {}'.format(vlan),
                    'description {}'.format(desc),
                    'ip address {}'.format(address),
                    'no ip redirects',
                    'no ip unreachables',
                    'hsrp version 2',
                    'hsrp {}'.format(vlan),
                    'preempt',
                    'ip {}'.format(standby)
                ]
                net_connect.send_config_set(commands)

                #  configure hsrp priority on router 1 only
                if 'vdc1' in host.get('device'):
                    net_connect.send_config_set([
                        'interface vlan {}'.format(vlan),
                        'hsrp {}'.format(vlan),
                        'priority 200'])

                print(net_connect.send_command('show run interface {}'.format(vlan)))

                #  cli output is parsed into a dictionary from returned text
                #  bgp variables set for configuration structure
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
                print(net_connect.send_command('show run | sec bgp'))

            elif change == 'rollback':

                #  interface commands to delete sub-interface and interface configurations
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

            #  save running configuration
            #  disconnect from the device
            output = net_connect.save_config()
            if 'startup-config' in output:
                output += net_connect.send_command_timing('\n')
            net_connect.disconnect()


if __name__ == '__main__':
    main()
