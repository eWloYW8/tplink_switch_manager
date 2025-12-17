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
        """配置 PortSettingRpm.htm"""
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
        data = {
            'groupId': port_id, 
            'portid': forward_port_list,
            'setapply': 'Apply'
        }
        self.get_action('port_isolation_set.cgi', data)

    def search_mac(self, mac):
        data = {'txt_macAddress_search': mac, 'apply': 'Search'}
        resp = self.get_action('mac_address_search.cgi', data)
        mac_ds = extract_js_variable(resp.text, 'mac_ds') or {}
        return mac_ds.get('mac_info', [])


    def create_port_trunk(self, lag_id, member_ports):
        """
        创建汇聚组 (LAG)
        :param lag_id: 1-8
        :param member_ports: 端口号列表，最多4个
        """
        if not (1 <= lag_id <= 8):
            raise ValueError("LAG ID must be between 1 and 8")
        
        if len(member_ports) < 2 or len(member_ports) > 4:
            raise ValueError("LAG members must be between 2 and 4 ports")

        data = {
            'groupId': lag_id,
            'portid': member_ports, # requests 会转为 portid=1&portid=2...
            'setapply': 'Apply'
        }
        self.get_action('port_trunk_set.cgi', data)

    def delete_port_trunk(self, lag_ids):
        """
        删除汇聚组
        :param lag_ids: 单个ID或ID列表
        """
        if isinstance(lag_ids, int):
            lag_ids = [lag_ids]
            
        if not lag_ids: return

        # HTML: <form name=port_trunk_display action=port_trunk_display.cgi>
        # 参数名: chk_trunk
        data = {
            'chk_trunk': lag_ids,
            'setDelete': 'Delete'
        }
        self.get_action('port_trunk_display.cgi', data)


    def set_mirror_destination(self, enable=True, dest_port_id=0):
        """
        设置镜像目的端口 (监控端口)
        :param enable: 是否开启
        :param dest_port_id: 目的端口号
        """
        # HTML: <form name=mirror_enabled_set action=mirror_enabled_set.cgi>
        data = {
            'state': 1 if enable else 0,
            'mirroringport': dest_port_id if enable else 0,
            'mirrorenable': 'Apply'
        }
        self.get_action('mirror_enabled_set.cgi', data)

    def set_mirror_source(self, source_ports, ingress=False, egress=False):
        """
        设置镜像源端口 (被监控端口)
        :param source_ports: 端口号列表
        :param ingress: 监控入流量
        :param egress: 监控出流量
        """
        if not source_ports: return

        # HTML: <form name=mirrored_port_set action=mirrored_port_set.cgi>
        # 参数: mirroredport (列表), ingressState, egressState
        data = {
            'mirroredport': source_ports,
            'ingressState': 1 if ingress else 0,
            'egressState': 1 if egress else 0,
            'mirrored_submit': 'Apply'
        }
        self.get_action('mirrored_port_set.cgi', data)