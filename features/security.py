from ..parsers import extract_js_variable

class SecurityMixin:
    def get_dhcp_snooping_config(self):
        """DhcpSnoopingRpm.htm"""
        html = self.get_page('DhcpSnoopingRpm.htm')
        ds = extract_js_variable(html, 'dhcp_ds') or {}
        
        # 提取端口配置
        ports = []
        trust = ds.get('trust', [])
        for i in range(self.max_ports):
            ports.append({
                "port": i+1,
                "trust": bool(trust[i])
            })
            
        return {
            "global_enable": bool(ds.get('state', 0)),
            "ports": ports
        }

    def set_dhcp_snooping_global(self, enable=True):
        data = {
            'dhcp_mode': 1 if enable else 0,
            'Apply': 'Apply'
        }
        self.post_action('dhcp_enable_set.cgi', data)

    def set_dhcp_snooping_port(self, port_id, trust=False):
        """dhcp_port_set.cgi"""
        # 该接口需要提交大量参数，通常是提交当前状态的完整快照或单口修改
        # 简化版：仅修改 Trust
        data = {
            'portSel': port_id, # 多选框
            'trustPort': 1 if trust else 0,
            'option82': 0, # 保持默认或需要从 get 中获取当前值
            'operation': 0,
            'dhcp_submit': 'Apply'
        }
        self.post_action('dhcp_port_set.cgi', data)
