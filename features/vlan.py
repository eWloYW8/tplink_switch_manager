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
        """
        添加或编辑 VLAN
        HTML Form: <form action=qvlanSet.cgi> (默认 GET)
        """
        # 注意: 提交按钮的值通常作为参数传递
        # 原始 HTML: <input type=submit value=添加/编辑 name=qvlan_add>
        # 为了兼容性，我们传递该参数，值设为 'Add/Edit' 或者是原始中文，
        # 但通常 CGI 只检查 key 是否存在。
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
                
        # 使用 GET 请求
        self.get_action('qvlanSet.cgi', params)
    
    def delete_8021q_vlan(self, vlan_ids):
        """
        [新增] 删除 802.1Q VLAN
        :param vlan_ids: 单个 VLAN ID (int) 或 VLAN ID 列表 (list[int])
        """
        if isinstance(vlan_ids, int):
            vlan_ids = [vlan_ids]

        if not vlan_ids:
            return

        # 构造参数
        # requests 库会自动将列表值转换为 multiple parameters:
        # selVlans=10&selVlans=20
        params = {
            'selVlans': vlan_ids,
            'qvlan_del': 'Delete'  # 触发删除动作的 key
        }
        
        # 使用 GET 请求 (修复 502 错误的关键)
        self.get_action('qvlanSet.cgi', params)

    def set_pvid(self, port_list, pvid):
        """Vlan8021QPvidRpm.htm"""
        pbm = 0
        for p in port_list:
            pbm |= (1 << (p-1))
        
        # URL: vlanPvidSet.cgi?pbm=...&pvid=...
        params = {'pbm': pbm, 'pvid': pvid}
        self.get_action('vlanPvidSet.cgi', params)