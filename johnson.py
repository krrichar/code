#!/usr/bin/python
# -*- coding: utf-8 -*-

from netmiko import ConnectHandler

args = {'username': 'developer', 'password': 'C1sco12345',
        'port': 8181, 'device_type': 'cisco_ios'}
change = input('change or rollback: ').lower()
hosts = [
    {
        'device': 'ios-xe-mgmt.cisco.com',
        'addr': '10.254.100.4',
        'interfaces': [
            'GigabitEthernet1',
            'GigabitEthernet2',
            'GigabitEthernet3'
            ],
        'record': 'liveaction-flowrecord',
        'exporter': 'liveaction-flowexporter-ipfix',
        'monitor': 'liveaction-flowmonitor',
        'destination': '10.25.4.79'
    }
]


def main():

    def netflow_config(record, exporter, monitor, destination):

        rec_config = [
            'flow record {}'.format(record),
            'description DO NOT MODIFY. USED BY LIVEACTION.',
            'match ipv4 tos',
            'match ipv4 protocol',
            'match ipv4 source address',
            'match ipv4 destination address',
            'match transport source-port',
            'match transport destination-port',
            'match interface input',
            'match flow direction',
            'collect routing source as',
            'collect routing destination as',
            'collect routing next-hop address ipv4',
            'collect ipv4 dscp',
            'collect ipv4 id',
            'collect ipv4 source prefix',
            'collect ipv4 source mask',
            'collect ipv4 destination mask',
            'collect transport tcp flags',
            'collect interface output',
            'collect flow sampler',
            'collect counter bytes',
            'collect counter packets',
            'collect timestamp sys-uptime first',
            'collect timestamp sys-uptime last',
            'collect application name',
            'collect application http host',
            'collect application ssl common-name',
            ]

        exp_config = [
            'flow exporter {}'.format(exporter),
            'description DO NOT MODIFY. USED BY LIVEACTION.',
            'destination {}'.format(destination),
            'source Loopback0',
            'transport udp 2055',
            'export-protocol ipfix',
            'option interface-table',
            'option vrf-table',
            'option c3pl-class-table',
            'option c3pl-policy-table',
            'option sampler-table',
            'option application-table',
            'option application-attributes',
            ]
        mon_config = [
            'flow monitor {}'.format(monitor),
            'description DO NOT MODIFY. USED BY LIVEACTION.',
            'exporter {}'.format(exporter),
            'cache timeout inactive 10',
            'cache timeout active 60',
            'record {}'.format(record),
            ]
        net_connect.send_config_set(rec_config)
        net_connect.send_config_set(exp_config)
        net_connect.send_config_set(mon_config)

    def interface_config(monitor, inet):

        inet_config = [
            'interface {}'.format(inet),
            'ip flow monitor {} input'.format(monitor),
            'ip flow monitor {} output'.format(monitor)            ]
        net_connect.send_config_set(inet_config)

    def acl_config(sequence):

        acl = [
            'ip access-list standard 55',
            '{} permit 10.25.4.79'.format(sequence)
            ]
        net_connect.send_config_set(acl)

    #  connect handler to log into each device in the devices list
    #  use for prechex to gather configuration backup

    for host in hosts:
        net_connect = ConnectHandler(host.get('device'), session_log=host.get('device'), **args)
        print(net_connect.send_config_set(net_connect.find_prompt()))
        net_connect.send_command('show run')
        output = net_connect.save_config()
        if 'startup-config' in output:
            output += net_connect.send_command_timing('\n')

        #  variables to be used for interface command structure

        n_record = host.get('record')
        n_exporter = host.get('exporter')
        n_monitor = host.get('monitor')
        n_destination = host.get('destination')
        n_interfaces = host.get('interfaces')
        n_sequence = '15'

        if change == 'change':

            #  functions to create netflow objects

            netflow_config(record=n_record, exporter=n_exporter, monitor=n_monitor, destination=n_destination)
            for interface in n_interfaces:
                interface_config(monitor=n_monitor, inet=interface)
            acl_config(sequence=n_sequence)

        elif change == 'rollback':

            #  removes previously configured netflow

            for interface in n_interfaces:
                rollback = [
                    'interface {}'.format(interface),
                    'no ip flow monitor {} input'.format(n_monitor),
                    'no ip flow monitor {} output'.format(n_monitor)
                    ]
                net_connect.send_config_set(rollback)

            rollback = [
                'no flow monitor {}'.format(n_monitor),
                'no flow exporter {}'.format(n_exporter),
                'no flow record {}'.format(n_record),
                'ip access-list standard 55', 'no 15'
                ]
            net_connect.send_config_set(rollback)

        #  save running configuration and disconnect from the device

        output = net_connect.save_config()
        if 'startup-config' in output:
            output += net_connect.send_command_timing('\n')
        net_connect.disconnect()


if __name__ == '__main__':
    main()
