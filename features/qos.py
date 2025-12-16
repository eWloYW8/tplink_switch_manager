from ..parsers import extract_js_variable

class QosMixin:
    def get_bandwidth_limits(self):
        """QosBandWidthControlRpm.htm"""
        html = self.get_page('QosBandWidthControlRpm.htm')
        # bcInfo 是扁平数组 [Ingress, Egress, LagID, Ingress, Egress, LagID...]
        bc = extract_js_variable(html, 'bcInfo') or []
        res = []
        for i in range(0, len(bc), 3):
            port = (i // 3) + 1
            if port > self.max_ports: break
            res.append({
                "port": port,
                "ingress": bc[i],
                "egress": bc[i+1]
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
        for i in range(0, len(sc), 3):
            port = (i // 3) + 1
            if port > self.max_ports: break
            type_mask = sc[i+1]
            res.append({
                "port": port,
                "rate": sc[i],
                "ul_frame": bool(type_mask & 1),
                "multicast": bool(type_mask & 2),
                "broadcast": bool(type_mask & 4),
                "enable": sc[i] > 0
            })
        return res
