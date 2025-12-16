# tplink_switch_manager/features/security.py
from ..parsers import extract_js_variable

class SecurityMixin:
    def get_dhcp_snooping_config(self):
        html = self.get_page('DhcpSnoopingRpm.htm')
        ds = extract_js_variable(html, 'dhcp_ds') or {}
        
        ports = []
        trust_list = ds.get('trust', [])
        
        for i in range(self.max_ports):
            is_trust = False
            if i < len(trust_list):
                is_trust = bool(trust_list[i])
            ports.append({ "port": i+1, "trust": is_trust })
            
        return {
            "global_enable": bool(ds.get('state', 0)),
            "ports": ports
        }

    def set_dhcp_snooping_global(self, enable=True):
        # <form name=dhcp_enable_set action=dhcp_enable_set.cgi ...> (Method 缺失 -> GET)
        data = {
            'dhcp_mode': 1 if enable else 0,
            'Apply': 'Apply'
        }
        self.get_action('dhcp_enable_set.cgi', data)

    def set_dhcp_snooping_port(self, port_id, trust=False):
        # <form name=dhcp_port_set action=dhcp_port_set.cgi ...> (Method 缺失 -> GET)
        data = {
            'dhcpport': port_id,
            'trustPort': 1 if trust else 0,
            'option82': 0, 
            'operation': 0,
            'dhcp_submit': 'Apply'
        }
        self.get_action('dhcp_port_set.cgi', data)