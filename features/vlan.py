# tplink_switch_manager/features/vlan.py
from ..parsers import extract_js_variable
from ..utils import bitmap_to_ports

class VlanMixin:
    def get_8021q_vlans(self):
        html = self.get_page('Vlan8021QRpm.htm')
        ds = extract_js_variable(html, 'qvlan_ds') or {}
        
        vlans = []
        count = ds.get('count', 0)
        vids = ds.get('vids', [])
        names = ds.get('names', [])
        tag = ds.get('tagMbrs', [])
        untag = ds.get('untagMbrs', [])
        
        real_count = min(count, len(vids), len(names))
        
        for i in range(real_count):
            vlans.append({
                "vid": vids[i],
                "name": names[i],
                "tagged": bitmap_to_ports(tag[i]),
                "untagged": bitmap_to_ports(untag[i])
            })
        return vlans

    def add_8021q_vlan(self, vid, name, tagged_ports=[], untagged_ports=[]):
        params = {
            'vid': vid,
            'vname': name,
            'qvlan_add': 'Add/Edit' 
        }
        
        for i in range(1, self.max_ports + 1):
            if i in tagged_ports:
                params[f'selType_{i}'] = 1 # Tag
            elif i in untagged_ports:
                params[f'selType_{i}'] = 0 # Untag
            else:
                params[f'selType_{i}'] = 2 # Non-member
                
        self.get_action('qvlanSet.cgi', params)
    
    def delete_8021q_vlan(self, vlan_ids):
        if isinstance(vlan_ids, int):
            vlan_ids = [vlan_ids]
        if not vlan_ids: return

        params = {
            'selVlans': vlan_ids,
            'qvlan_del': 'Delete'
        }
        self.get_action('qvlanSet.cgi', params)

    def set_pvid(self, port_list, pvid):
        pbm = 0
        for p in port_list:
            pbm |= (1 << (p-1))
        params = {'pbm': pbm, 'pvid': pvid}
        self.get_action('vlanPvidSet.cgi', params)

    def set_mtu_vlan_global(self, enable=True):
        """启用/禁用 MTU VLAN"""
        # VlanMtuRpm.htm: <form action=mtuVlanSet.cgi>
        data = {
            'mtu_en': 1 if enable else 0,
            'mtu_mode': 'Apply'
        }
        self.get_action('mtuVlanSet.cgi', data)

    def set_mtu_vlan_uplink(self, uplink_port_id):
        """设置 MTU VLAN 的 Uplink 端口"""
        data = {
            'uplinkPort': uplink_port_id,
            'mtu_uplink': 'Apply'
        }
        self.get_action('mtuVlanSet.cgi', data)


    def set_port_based_vlan_global(self, enable=True):
        """启用/禁用 端口 VLAN"""
        # VlanPortBasicRpm.htm: <form action=pvlanSet.cgi>
        data = {
            'pvlan_en': 1 if enable else 0,
            'pvlan_mode': 'Apply'
        }
        self.get_action('pvlanSet.cgi', data)

    def add_port_based_vlan(self, vlan_index, member_ports):
        """
        添加端口 VLAN 组
        :param vlan_index: 索引 1-N
        :param member_ports: 端口号列表
        """
        data = {
            'vid': vlan_index,
            'selPorts': member_ports,
            'pvlan_add': 'Apply'
        }
        self.get_action('pvlanSet.cgi', data)