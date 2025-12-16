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
        
        for i in range(count):
            vlans.append({
                "vid": vids[i],
                "name": names[i],
                "tagged": bitmap_to_ports(tag[i]),
                "untagged": bitmap_to_ports(untag[i])
            })
        return vlans

    def add_8021q_vlan(self, vid, name, tagged_ports=[], untagged_ports=[]):
        """添加或编辑 VLAN"""
        data = {
            'vid': vid,
            'vname': name,
            'qvlan_add': 'Add/Edit'
        }
        # 构建 selType_X 参数: 0=Untag, 1=Tag, 2=Non
        for i in range(1, self.max_ports + 1):
            if i in tagged_ports:
                data[f'selType_{i}'] = 1
            elif i in untagged_ports:
                data[f'selType_{i}'] = 0
            else:
                data[f'selType_{i}'] = 2
        self.post_action('qvlanSet.cgi', data)

    def set_pvid(self, port_list, pvid):
        """Vlan8021QPvidRpm.htm"""
        # 需要计算 port bitmap (sel_X) 和 pbm
        pbm = 0
        for p in port_list:
            pbm |= (1 << (p-1))
            
        # URL 提交方式比较特殊: vlanPvidSet.cgi?pbm=...&pvid=...
        url = f"vlanPvidSet.cgi?pbm={pbm}&pvid={pvid}"
        self.get_page(url) # 这里实际上是 GET 请求触发 CGI
