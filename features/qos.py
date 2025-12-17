# tplink_switch_manager/features/qos.py
from ..parsers import extract_js_variable

class QosMixin:
    def get_bandwidth_limits(self):
        html = self.get_page('QosBandWidthControlRpm.htm')
        bc = extract_js_variable(html, 'bcInfo') or []
        res = []
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
        html = self.get_page('QosStormControlRpm.htm')
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
        type_mask = 0
        if ul_frame: type_mask |= 1
        if multicast: type_mask |= 2
        if broadcast: type_mask |= 4
        
        data = {
            'rate': rate,
            'stormType': type_mask, 
            'state': 1 if enable else 0, 
            'applay': 'Apply',
            f'sel_{port_id}': 1
        }
        self.post_action('qos_storm_set.cgi', data)

    def set_qos_mode(self, mode):
        """
        设置全局 QoS 模式
        :param mode: 0=Port Based, 1=802.1P Based, 2=DSCP Based
        """
        # QosBasicRpm.htm: <form name=qos_mode_set method=post action=qos_mode_set.cgi>
        if mode not in [0, 1, 2]:
            raise ValueError("Mode must be 0, 1, or 2")
            
        data = {
            'rd_qosmode': mode,
            'qosmode': 'Apply'
        }
        self.post_action('qos_mode_set.cgi', data)

    def set_port_priority(self, port_id, priority_queue):
        """
        设置端口优先级 (仅在 Port Based 模式下有效)
        :param priority_queue: 0=Lowest, 1=Normal, 2=Medium, 3=Highest
        """
        # QosBasicRpm.htm: <form name=qos_port_priority_set method=post action=qos_port_priority_set.cgi>
        if priority_queue not in [0, 1, 2, 3]:
            raise ValueError("Priority must be 0-3")

        data = {
            f'sel_{port_id}': 1,
            'port_queue': priority_queue,
            'apply': 'Apply'
        }
        self.post_action('qos_port_priority_set.cgi', data)