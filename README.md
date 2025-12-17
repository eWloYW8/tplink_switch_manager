# TP-Link Switch Manager

```python
from tplink_switch_manager import TPLinkSwitchClient
import json


my_cookies = {
    'aaa': 'bbb'
}

sw = TPLinkSwitchClient("https://swc.example.com", "username", "password", extra_cookies=my_cookies)

try:
    sw.login()
    print("Login successful!")

    # 1. Get Port Status
    ports = sw.get_ports()
    print(f"Port Status:")
    for port in ports:
        print(json.dumps(port, indent=4))

    vlans = sw.get_8021q_vlans()
    print(f"Current VLANs:")
    for vlan in vlans:
        print(json.dumps(vlan, indent=4))
    
    bandwidth_limits = sw.get_bandwidth_limits()
    print(f"Bandwidth Limits:")
    print(json.dumps(bandwidth_limits, indent=4))

    # 2. Configure a VLAN
    # Add VLAN 1002, Port 24 tagged, Ports 1-3 untagged
    sw.add_8021q_vlan(1002, "test_VLAN", tagged_ports=[24], untagged_ports=[1,2,3])

    sw.delete_8021q_vlan(1002)
    
    # 3. Configure DHCP Snooping
    sw.set_dhcp_snooping_global(False)
    sw.set_dhcp_snooping_port(24, trust=False)

    # and others
    
except Exception as e:
    print(f"An error occurred: {e}")
```