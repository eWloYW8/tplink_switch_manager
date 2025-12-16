from ..parsers import extract_js_variable
from ..constants import SPEED_MAP
from ..utils import bitmap_to_ports, ports_to_bitmap

class SwitchingMixin:
    def get_ports(self):
        html = self.get_page('MainRpm.htm')
        p_info = extract_js_variable(html, 'port_info') or {}
        res = []
        for i in range(self.max_ports):
            res.append({
                "id": i+1,
                "state": "Up" if p_info['state'][i] else "Down",
                "speed_cfg": SPEED_MAP.get(p_info['spd_cfg'][i], "Unknown"),
                "speed_act": SPEED_MAP.get(p_info['spd_act'][i], "Down"),
                "rx": p_info['rx_rate'][i],
                "tx": p_info['tx_rate'][i]
            })
        return res

    def set_port_config(self, port_id, enable=True, speed=1, flow_ctrl=False):
        """配置 PortSettingRpm.htm"""
        data = {
            'portid': port_id,
            'state': 1 if enable else 0,
            'speed': speed, # 1=Auto
            'flowcontrol': 1 if flow_ctrl else 0,
            'apply': 'Apply'
        }
        self.post_action('port_setting.cgi', data)

    def get_port_isolation(self):
        """解析 PortIsolationRpm.htm"""
        html = self.get_page('PortIsolationRpm.htm')
        conf = extract_js_variable(html, 'portIso_conf') or {}
        isolation_list = []
        if 'port_iso' in conf:
            for i, bitmap in enumerate(conf['port_iso']):
                isolation_list.append({
                    "port": i+1,
                    "forward_ports": bitmap_to_ports(bitmap)
                })
        return isolation_list

    def set_port_isolation(self, port_id, forward_port_list):
        """设置端口隔离 (单口设置)"""
        # Port Isolation 设置通常是一个组提交，这里模拟选中一个端口设置其转发列表
        # 注意：TP-Link 该页面通常提交 groupId (被选端口) 和 portid (转发端口列表)
        data = {
            'groupId': port_id, # 这里 groupId 其实是被配置的端口
            'portid': forward_port_list, # 这是一个列表，requests 会处理为多个 portid 参数
            'setapply': 'Apply'
        }
        self.post_action('port_isolation_set.cgi', data)

    def search_mac(self, mac):
        """MacSearchRpm.htm"""
        data = {'txt_macAddress_search': mac, 'apply': 'Search'}
        resp = self.post_action('mac_address_search.cgi', data)
        mac_ds = extract_js_variable(resp.text, 'mac_ds') or {}
        return mac_ds.get('mac_info', [])
