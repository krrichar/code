#!/usr/bin/env python
# -*- coding: utf-8 -*-

from netmiko import ConnectHandler
from getpass import getpass
from paramiko import SSHException
import sys

password = getpass()
change_type = input('change or rollback: ').lower()
args = {'username': 'krrichar', 'password': password,
        'device_type': 'cisco_nxos'}

hosts = ['us6645ny-ppcore-vdc1',
         'us6647ny-ppcore-vdc1']

wdc = {'site': '6645',
       'vlan_id': '900',
       'vlan_name': 'VL900_WDC_N2A_192.0.6.5/24',
       'interfaces': 'Ethernet1/3, Ethernet1/6, Ethernet1/10-13,\
                      Ethernet5/3, Ethernet5/6, Ethernet5/10-13'}
hdc = {'site': '6647',
       'vlan_id': '900',
       'vlan_name': 'VL900_HDC_N2A_192.1.6.5/24',
       'interfaces': 'Ethernet1/3, Ethernet1/6-7, Ethernet1/10, Ethernet1/12, Ethernet1/15,\
                      Ethernet5/3, Ethernet5/6-7, Ethernet5/10, Ethernet5/12, Ethernet5/15'}


def main():


    def change(vlan_id, name, interface):
        """
        @param vlan_id: vlan id -> str
        @param name: vlan name -> str
        @param interface: trunk interface(s) to add vlan -> list
        @return: None
        """
        net_connect = ConnectHandler(host, session_log=host, **args)
        print(net_connect.find_prompt())
        net_connect.send_command('show run')
        precheck = net_connect.send_command('show vlan id {}'.format(vlan_id))
        if 'active' in precheck:
            print('\n\t## vlan already exists ##')
            sys.exit()
        net_connect.send_config_set(['vlan {}'.format(vlan_id),
                                     'name {}'.format(name),
                                     'interface {}'.format(interface),
                                     'switchport trunk allowed vlan add {}'.format(vlan_id)])
        postcheck = net_connect.send_command('show vlan id {}'.format(vlan_id))
        print(postcheck)
        net_connect.send_command('copy running-config startup-config')
        net_connect.disconnect()


    def rollback(vlan_id, interface):
        """
        @param num: vlan id -> str
        @param interface: trunk interface(s) to add vlan -> str
        @return: None
        """
        net_connect = ConnectHandler(host, session_log=host, **args)
        print(net_connect.find_prompt())
        net_connect.send_command('show run')
        precheck = net_connect.send_command('show vlan id {}'.format(vlan_id))
        if 'not found' in precheck:
            print('\n\t## vlan is not present ##')
            sys.exit()
        net_connect.send_config_set(['no vlan {}'.format(vlan_id),
                                     'interface {}'.format(interface),
                                     'switchport trunk allowed vlan remove {}'.format(vlan_id)])
        postcheck = net_connect.send_command('show vlan id {}'.format(vlan_id))
        print(postcheck)
        net_connect.send_command('copy running-config startup-config')
        net_connect.disconnect()


    for host in hosts:
        #  webster
        try:
            if (wdc['site'] in host) and (change_type == 'change'):
                change(num=wdc['vlan_id'], name=wdc['vlan_name'], interface=wdc['interfaces'])
            elif (wdc['site'] in host) and (change_type == 'rollback'):
                rollback(num=wdc['vlan_id'], interface=wdc['interfaces'])
        except (EOFError, SSHException) as error:
            print(error, '\n\t## webster changes unsuccessful ##')
        #  henrietta
        try:
            if (hdc['site']' in host) and (change_type == 'change'):
                change(num=wdc['vlan_id'], name=wdc['vlan_name'], interface=wdc['interfaces'])
            elif (hdc['site'] in host) and (change_type == 'rollback'):
                rollback(num=hdc['vlan_id'], interface=hdc['interfaces'])
        except (EOFError, SSHException) as error:
            print(error, '\n\t## henrietta changes unsuccessful ##')
        print('\n\t## changes complete for {} ##'.format(host))


if __name__ == '__main__':
    main()
