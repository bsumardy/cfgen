**vEOS Underlay Network Configuration Generator**

This project uses an Ansible playbook to automate the generation of vEOS configuration files for a leaf-spine underlay network topology. It is primarily intended for lab environments, but it can also be adapted for real-world deployments (e.g., new site or data center rollouts).


**Features**
Auto-generates configuration for:
1. Leaf switches with MLAG enabled
2. Spine switches
3. OSPF is configured on all switches
4. Auto-assigns subnets for various purposes:
- Loopback0: 10.1.14.0/24
- P2P Links: 10.1.15.0/24
- LAN Subnets: 10.1.0.0/21
5. Network base: 10.1.0.0/20
6. All device-specific variables are generated and stored under /host_vars
7. Templates for each role are found in /roles/{leaf,spine}/templates
8. Final configurations are saved to /generated_configs

**Usage**
Run the playbook with your desired topology:

_ansible-playbook generate_all.yml -e "leaf_count=4 spine_count=2"_ 
This command generates configurations for 4 leaf and 2 spine switches. Replace leaf_count and spine_count as per needed.

**Lab vs Production**
- Lab: Currently used for lab simulations with vEOS.
- Production: Ready to be adapted for real environment deployments (e.g., data centers or remote sites).
