# tplink_switch_manager/features/qos.py
from ..parsers import extract_js_variable

class QosMixin:
    def get_bandwidth_limits(self):
        """QosBandWidthControlRpm.htm"""
        html = self.get_page('QosBandWidthControlRpm.htm')
        # bcInfo: [Ingress, Egress, LagID, Ingress, Egress, LagID...]
        bc = extract_js_variable(html, 'bcInfo') or []
        res = []
        # 每3个一组
        count = len(bc) // 3
        for i in range(count):
            port = i + 1
            if port > self.max_ports: break
            base = i * 3
            res.append({
                "port": port,
                "ingress": bc[base],
                "egress": bc[base+1]
            })
        return res

    def set_bandwidth_limit(self, port_id, ingress, egress):
        data = {
            'igrRate': ingress,
            'egrRate': egress,
            'applay': 'Apply',
            f'sel_{port_id}': 1
        }
        self.post_action('qos_bandwidth_set.cgi', data)

    def get_storm_control(self):
        """QosStormControlRpm.htm"""
        html = self.get_page('QosStormControlRpm.htm')
        # scInfo: [Rate, TypeMask, LagID, ...]
        sc = extract_js_variable(html, 'scInfo') or []
        res = []
        count = len(sc) // 3
        for i in range(count):
            port = i + 1
            if port > self.max_ports: break
            base = i * 3
            rate = sc[base]
            type_mask = sc[base+1]
            
            res.append({
                "port": port,
                "rate": rate,
                "ul_frame": bool(type_mask & 1),
                "multicast": bool(type_mask & 2),
                "broadcast": bool(type_mask & 4),
                "enable": rate > 0 and type_mask > 0
            })
        return res
        
    def set_storm_control(self, port_id, rate, ul_frame=False, multicast=False, broadcast=False, enable=True):
        """
        修正：添加了缺失的 state 参数
        """
        type_mask = 0
        if ul_frame: type_mask |= 1
        if multicast: type_mask |= 2
        if broadcast: type_mask |= 4
        
        data = {
            'rate': rate,
            'stormType': type_mask, # 这是一个 multi-select，CGI 通常接受位图值或数组
            'state': 1 if enable else 0, # 关键修复：添加 state
            'applay': 'Apply',
            f'sel_{port_id}': 1
        }
        self.post_action('qos_storm_set.cgi', data)