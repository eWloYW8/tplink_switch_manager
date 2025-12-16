# tplink_switch_manager/features/switching.py
from ..parsers import extract_js_variable
from ..constants import SPEED_MAP
from ..utils import bitmap_to_ports

class SwitchingMixin:
    def get_ports(self):
        html = self.get_page('MainRpm.htm')
        p_info = extract_js_variable(html, 'port_info') or {}
        
        res = []
        if 'state' in p_info:
            for i in range(self.max_ports):
                if i >= len(p_info['state']): break
                
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
        """
        配置 PortSettingRpm.htm
        HTML: <form name=port_setting action=port_setting.cgi enctype=...> (Method 缺失 -> GET)
        """
        data = {
            'portid': port_id,
            'state': 1 if enable else 0,
            'speed': speed, # 1=Auto
            'flowcontrol': 1 if flow_ctrl else 0,
            'apply': 'Apply'
        }
        self.get_action('port_setting.cgi', data)

    def get_port_isolation(self):
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
        """
        设置端口隔离
        HTML: <form name=port_trunk_set action=port_isolation_set.cgi> (Method 缺失 -> GET)
        """
        data = {
            'groupId': port_id, 
            'portid': forward_port_list,
            'setapply': 'Apply'
        }
        self.get_action('port_isolation_set.cgi', data)

    def search_mac(self, mac):
        """MacSearchRpm.htm (Method 缺失 -> GET)"""
        data = {'txt_macAddress_search': mac, 'apply': 'Search'}
        # 这里实际上返回的是页面 HTML，不仅是动作，所以用 get_page_raw 带参数更合适
        # 或者用 get_action 获取响应后解析
        resp = self.get_action('mac_address_search.cgi', data)
        mac_ds = extract_js_variable(resp.text, 'mac_ds') or {}
        return mac_ds.get('mac_info', [])