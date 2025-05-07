#!/usr/bin/env python3

import os
import sys
import yaml
import random
from ipaddress import ip_network

def generate_vars(leaf_count, spine_count):
    if leaf_count > 16 or spine_count > 4:
        raise ValueError("Max 16 leafs and 4 spines are supported.")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    host_vars_dir = os.path.join(base_dir, 'host_vars')
    group_vars_dir = os.path.join(base_dir, 'group_vars')

    os.makedirs(host_vars_dir, exist_ok=True)
    os.makedirs(group_vars_dir, exist_ok=True)

    uplink_pool = list(ip_network("10.1.15.0/24").subnets(new_prefix=31))
    loopback_pool = list(ip_network("10.1.14.0/24").hosts())
    vlan10_pool = list(ip_network("10.1.0.0/21").subnets(new_prefix=26))
    
    # Generate Spine configs
    for i in range(spine_count):
        hostname = f"spine{i+1}"
        loopback_ip = str(loopback_pool.pop(0)) + "/32"
        interfaces = {}

        for j in range(leaf_count):
            iface = f"Ethernet{j+1}"
            uplink_subnet = uplink_pool[i * leaf_count + j]
            ip = str(uplink_subnet[1]) + "/31"
            interfaces[iface] = {
                "description": f"To {hostname} <-> leaf{j+1}",
                "ip": ip
            }

        data = {
            "hostname": hostname,
            "interfaces": interfaces,
            "loopback_ip": loopback_ip
        }

        with open(os.path.join(host_vars_dir, f"{hostname}.yml"), 'w') as f:
            yaml.dump(data, f)

    # Generate Leaf configs
    for i in range(leaf_count):
        hostname = f"leaf{i+1}"
        loopback_ip = str(loopback_pool.pop(0)) + "/32"
        vlan_subnet = vlan10_pool[i // 2]
        vlan_ip = vlan_subnet[-4] if i % 2 == 0 else vlan_subnet[-3]
        vr_ip = vlan_subnet[-2]        
        mlag_subnet = ["192.168.0.0", "192.168.0.1"]
        mlag_ip = str(mlag_subnet[0])
        mlag_peer_ip = str(mlag_subnet[1])        
        if i % 2 != 0:  # Check if i is odd
            mlag_ip, mlag_peer_ip = mlag_peer_ip, mlag_ip
        interfaces = {
            "Ethernet1": {
                "description": "MLAG Peer",
                "trunk": True
            },
            "Vlan10": {
                "description": "User LAN",
                "ip": str(vlan_ip) + "/26",
                "vr_ip": str(vr_ip)                
            },
            "Vlan4094": {
                "description": "MLAG Virtual Interface",
                "ip": mlag_ip + "/31"
            },
            "Loopback0": {
                "description": "Router ID",
                "ip": loopback_ip
            }
        }

        # Uplinks to spines
        for j in range(spine_count):
            iface = f"Ethernet{j+2}"
            uplink_subnet = uplink_pool[j * leaf_count + i]
            ip = str(uplink_subnet[0]) + "/31"
            interfaces[iface] = {
                "description": f"Uplink to spine{j+1}",
                "ip": ip
            }

        data = {
            "hostname": hostname,
            "interfaces": interfaces,
            "loopback_ip": loopback_ip,
            "mlag_domain": "MLAG1",
            "mlag_ip": mlag_ip,
            "mlag_peer_ip": mlag_peer_ip,
            "vlan10_ip": str(vlan_ip) + "/26",
            "vlan10_virtual_ip": str(vr_ip)            
        }

        with open(os.path.join(host_vars_dir, f"{hostname}.yml"), 'w') as f:
            yaml.dump(data, f)

    # Group Vars
    with open(os.path.join(group_vars_dir, "all.yml"), 'w') as f:
        yaml.dump({"ospf_area": 0}, f)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_vars.py <leaf_count> <spine_count>")
        sys.exit(1)

    generate_vars(int(sys.argv[1]), int(sys.argv[2]))