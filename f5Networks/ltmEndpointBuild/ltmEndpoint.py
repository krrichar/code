#! /usr/bin/env python
"""
This script will build ltm endpoints by taking command line arguments
that specify the hostname and the resource file you'd like to use.  The 
resource file must be in YAML format.  Credentials use the admin account
and will prompt for the password.

syntax:
python <script_name> <hostname> <YAML_file>

example:
python ltmEndpoint.py lab-ltm schema.yaml
"""
from f5.bigip import ManagementRoot
from getpass import getpass
import sys
import yaml

USER = input('Username: ')
PASSWORD = getpass()

session = ManagementRoot(sys.argv[1], USER, PASSWORD, token=True)

with open(sys.argv[2]) as f:
    yaml_dict = yaml.safe_load(f)


def node():
    for node in yaml_dict["nodes"]:
        cmd = session.tm.ltm.nodes.node.create(
            name=node["name"], address=node["address"], partition="Common"
        )
    pool()


def pool():
    for pool in yaml_dict["pools"]:
        cmd = session.tm.ltm.pools.pool.create(
            name=pool["name"], monitor=pool["monitor"]
        )
        pool_load = session.tm.ltm.pools.pool.load(name=pool["name"])
        for member in pool["members"]:
            sub_cmd = pool_load.members_s.members.create(
                name=member["name"] + ":" + member["port"], partition="Common"
            )
    virtual()


def virtual():
    for virtual in yaml_dict["virtual_servers"]:
        params = {
            "name": virtual["name"],
            "destination": virtual["destination"],
            "mask": virtual["mask"],
            "ipProtocol": virtual["ipProtocol"],
            "pool": virtual["pool"],
            "profiles": virtual["profiles"],
            "partition": "Common",
            "sourceAddressTranslation": virtual["sourceAddressTranslation"],
        }
    cmd = session.tm.ltm.virtuals.virtual.create(**params)


if __name__ == "__main__":
    node()
