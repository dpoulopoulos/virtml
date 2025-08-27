#!/usr/bin/env python3
"""
Interactive Ansible Inventory Generator for VirtML

This script generates the ansible/inventory/hosts.yml file by asking the user
interactive questions about their infrastructure setup.
"""

import ipaddress
import re
import sys
from pathlib import Path
from typing import Dict, List

try:
    from jinja2 import Template
    from ruamel.yaml import YAML
except ImportError as e:
    print(f"Error: Missing required dependency: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)


# Jinja2 template for hosts.yml
HOSTS_TEMPLATE = """---
all:
  hosts:
    {{ admin_host }}:
{%- for node in nodes %}
    {{ node.name }}:
      ip: {{ node.ip }}
      ansible_host: {{ node.ip }}
{%- endfor %}
  children:
    libvirt:
      hosts:
{%- for node in nodes %}
        {{ node.name }}:
          virt_domain_name: {{ node.name }}
{%- endfor %}
    kubernetes:
      hosts:
{%- for node in nodes %}
        {{ node.name }}:
{%- endfor %}
    kubemasters:
      hosts:
{%- for node in nodes[:masters_count] %}
        {{ node.name }}:
{%- endfor %}
    k8s_cluster:
      children:
        kubernetes:
    kube_node:
      children:
        kubernetes:
    kube_control_plane:
      children:
        kubemasters:
    etcd:
      children:
        kubemasters:
    kubespray:
      children:
        kubernetes:
    admin:
      hosts:
        {{ admin_host }}:
"""

# Template for host_vars/boogie/boogie.yml
HOST_VARS_TEMPLATE = """# Ansible will SSH into managed machines as this user
ansible_user: {{ ansible_user }}

# Local user on the control machine
user: {{ user }}
"""

# Template for group_vars/libvirt/libvirt.yml
GROUP_VARS_TEMPLATE = """---
virt_host: {{ admin_host }}
virt_domain_disk_gb: {{ disk_gb }}
virt_domain_num_vcpus: {{ vcpus }}
virt_domain_memory_mb: {{ memory_mb }}
virt_domain_net_bridge: {{ network_bridge }}

# Ansible will SSH into managed machines as this user
ansible_user: {{ ansible_user }}

# Local user on the control machine
user: {{ user }}
"""


class InventoryGenerator:
    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        
    def _validate_hostname(self, hostname: str) -> bool:
        """Validate hostname format."""
        if len(hostname) > 63 or not hostname:
            return False
        if hostname.startswith('-') or hostname.endswith('-'):
            return False
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'
        return bool(re.match(pattern, hostname))
    
    def get_admin_host(self) -> str:
        """Get admin host name from user."""
        while True:
            admin_host = input("Enter admin host name (up to 64 characters): ").strip()
            if not admin_host:
                print("Invalid hostname. "
                      "Please use only letters, numbers, and hyphens and keep it under 64 characters.")
            else:
                if self._validate_hostname(admin_host):
                    return admin_host
                else:
                    print("Invalid hostname. "
                          "Please use only letters, numbers, and hyphens and keep it under 64 characters.")
    
    def get_node_count(self) -> int:
        """Get number of Kubernetes nodes from user."""
        while True:
            try:
                count_str = input("Enter number of Kubernetes nodes [5]: ").strip()
                if not count_str:
                    return 5
                count = int(count_str)
                if 1 <= count <= 50:
                    return count
                else:
                    print("Please enter a number between 1 and 50.")
            except ValueError:
                print("Please enter a valid number.")
    
    def get_masters_count(self, total_nodes: int) -> int:
        """Get number of master nodes from user."""
        max_masters = min(total_nodes, 7)  # Odd number recommended, max 7
        default_masters = min(3, total_nodes)
        
        while True:
            try:
                count_str = input(
                    f"Enter number of master nodes [1-{max_masters}, default: {default_masters}]: ").strip()
                if not count_str:
                    return default_masters
                count = int(count_str)
                if 1 <= count <= max_masters:
                    if count % 2 == 0:
                        print("Warning: Even number of masters can cause split-brain issues in etcd.")
                        confirm = input("Continue anyway? [y/N]: ").strip().lower()
                        if confirm not in ('y', 'yes'):
                            continue
                    return count
                else:
                    print(f"Please enter a number between 1 and {max_masters}.")
            except ValueError:
                print("Please enter a valid number.")
    
    def get_network_cidr(self) -> tuple:
        """Get network CIDR from user."""
        while True:
            cidr = input("Enter network CIDR [192.168.20.0/24]: ").strip()
            if not cidr:
                cidr = "192.168.20.0/24"
            
            try:
                network = ipaddress.IPv4Network(cidr, strict=False)
                # Extract base IP (first three octets for /24)
                ip_base = '.'.join(str(network.network_address).split('.')[:-1])
                return ip_base, network
            except ipaddress.AddressValueError:
                print("Invalid CIDR. Please enter in format like '192.168.20.0/24'")
    
    def get_starting_ip(self) -> int:
        """Get starting IP number from user."""
        while True:
            try:
                start_str = input("Enter starting IP number [1]: ").strip()
                if not start_str:
                    return 1
                start = int(start_str)
                if 1 <= start <= 254:
                    return start
                else:
                    print("Please enter a number between 1 and 254.")
            except ValueError:
                print("Please enter a valid number.")
    
    def get_vm_specs(self) -> dict:
        """Get VM specifications from user."""
        specs = {}
        
        # Get disk size
        while True:
            try:
                disk_str = input("Enter VM disk size in GB [128]: ").strip()
                if not disk_str:
                    specs['disk_gb'] = 128
                    break
                disk = int(disk_str)
                if 10 <= disk <= 2000:
                    specs['disk_gb'] = disk
                    break
                else:
                    print("Please enter a disk size between 10 and 2000 GB.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get vCPUs
        while True:
            try:
                vcpu_str = input("Enter number of vCPUs per VM [4]: ").strip()
                if not vcpu_str:
                    specs['vcpus'] = 4
                    break
                vcpus = int(vcpu_str)
                if 1 <= vcpus <= 32:
                    specs['vcpus'] = vcpus
                    break
                else:
                    print("Please enter vCPUs between 1 and 32.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get memory
        while True:
            try:
                memory_str = input("Enter VM memory in MB [16384]: ").strip()
                if not memory_str:
                    specs['memory_mb'] = 16384
                    break
                memory = int(memory_str)
                if 512 <= memory <= 131072:
                    specs['memory_mb'] = memory
                    break
                else:
                    print("Please enter memory between 512 MB and 128 GB (131072 MB).")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get network bridge
        bridge = input("Enter network bridge name [br0]: ").strip()
        specs['network_bridge'] = bridge if bridge else "br0"
        
        return specs
    
    def get_user_config(self) -> dict:
        """Get user configuration."""
        config = {}
        
        # Get ansible user
        ansible_user = input("Enter ansible user [root]: ").strip()
        config['ansible_user'] = ansible_user if ansible_user else "root"
        
        # Get local user
        user = input("Enter local user [root]: ").strip()
        config['user'] = user if user else "root"
        
        return config
    
    def generate_nodes(self, count: int, ip_base: str, start_ip: int, network: ipaddress.IPv4Network) -> List[Dict[str, str]]:
        """Generate node configuration."""
        nodes = []
        for i in range(count):
            node_num = i + 1
            ip_num = start_ip + i
            full_ip = f'{ip_base}.{ip_num}'
            
            # Validate IP is within network range
            try:
                ip_addr = ipaddress.IPv4Address(full_ip)
                if ip_addr not in network:
                    print(f"Warning: IP {full_ip} is outside the network {network}. Consider adjusting the starting IP.")
            except ipaddress.AddressValueError:
                print(f"Warning: Invalid IP {full_ip} generated.")
            
            nodes.append({
                'name': f'node{node_num}',
                'ip': full_ip
            })
        return nodes
    
    def preview_inventory(self, content: str) -> bool:
        """Show preview and ask for confirmation."""
        print("\n" + "="*60)
        print("PREVIEW OF GENERATED INVENTORY:")
        print("="*60)
        print(content)
        print("="*60)
        
        while True:
            confirm = input("\nDoes this look correct? [Y/n]: ").strip().lower()
            if confirm in ('', 'y', 'yes'):
                return True
            elif confirm in ('n', 'no'):
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    def save_file(self, content: str, file_path, description: str, ask_confirmation: bool = False) -> bool:
        """Save content to file with optional user confirmation."""
        output_path = file_path
        
        if ask_confirmation:
            while True:
                save_choice = input(f"\nSave to {file_path}? [Y/n/custom]: ").strip().lower()
                
                if save_choice in ('', 'y', 'yes'):
                    output_path = file_path
                    break
                elif save_choice in ('n', 'no'):
                    return False
                elif save_choice in ('c', 'custom'):
                    custom_path = input("Enter custom path: ").strip()
                    if not custom_path:
                        continue
                    output_path = custom_path
                    break
                else:
                    print("Please enter 'y' for yes, 'n' for no, or 'custom' for custom path.")
        
        try:
            # Create directory if it doesn't exist
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(content)
            
            print(f"{description} saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error saving {description.lower()}: {e}")
            return False
    
    def run(self):
        """Run the interactive inventory generation."""
        print("VirtML Ansible Inventory Generator")
        print("==================================")
        print()
        
        # Gather basic information
        admin_host = self.get_admin_host()
        node_count = self.get_node_count()
        masters_count = self.get_masters_count(node_count)
        ip_base, network = self.get_network_cidr()
        start_ip = self.get_starting_ip()
        
        # Gather VM specifications
        print("\nVM Configuration:")
        vm_specs = self.get_vm_specs()
        
        # Gather user configuration
        print("\nUser Configuration:")
        user_config = self.get_user_config()
        
        # Generate nodes
        nodes = self.generate_nodes(node_count, ip_base, start_ip, network)
        
        # Prepare template variables
        template_vars = {
            'admin_host': admin_host,
            'nodes': nodes,
            'masters_count': masters_count,
            **vm_specs,
            **user_config
        }
        
        # Render templates
        inventory_template = Template(HOSTS_TEMPLATE)
        inventory_content = inventory_template.render(**template_vars)
        
        host_vars_template = Template(HOST_VARS_TEMPLATE)
        host_vars_content = host_vars_template.render(**template_vars)
        
        group_vars_template = Template(GROUP_VARS_TEMPLATE)
        group_vars_content = group_vars_template.render(**template_vars)
        
        # Preview and save
        if self.preview_inventory(inventory_content):
            # Use pathlib to calculate paths relative to this script
            script_path = Path(__file__)
            repo_dir = script_path.parent.parent.parent  # Go up from scripts directory
            inventory_dir = repo_dir / "ansible" / "inventory"
            
            # Define file paths
            hosts_path = inventory_dir / "hosts.yml"
            host_vars_path = inventory_dir / "host_vars" / admin_host / f"{admin_host}.yml"
            group_vars_path = inventory_dir / "group_vars" / "libvirt" / "libvirt.yml"
            
            # Save all files
            success = True
            success &= self.save_file(inventory_content, hosts_path, "Inventory", ask_confirmation=True)
            success &= self.save_file(host_vars_content, host_vars_path, f"Host variables for {admin_host}")
            success &= self.save_file(group_vars_content, group_vars_path, "Libvirt group variables")
            
            if success:
                print(f"\nAll configuration files generated successfully!")
                print(f"Generated files:")
                print(f"  - {hosts_path}")
                print(f"  - {host_vars_path}")
                print(f"  - {group_vars_path}")
        else:
            print("Generation cancelled.")


if __name__ == "__main__":
    generator = InventoryGenerator()
    try:
        generator.run()
    except KeyboardInterrupt:
        print("\n\nGeneration cancelled by user.")
        sys.exit(1)
