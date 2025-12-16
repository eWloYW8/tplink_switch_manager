from ..parsers import extract_js_variable

class MonitoringMixin:
    def get_cable_diag(self):
        """CableDiagRpm.htm"""
        html = self.get_page('CableDiagRpm.htm')
        states = extract_js_variable(html, 'cablestate') or []
        lengths = extract_js_variable(html, 'cablelength') or []
        res = []
        state_map = {0: "No Cable", 1: "Normal", 2: "Open", 3: "Short"}
        for i in range(len(states)):
            if states[i] == -1: continue
            res.append({
                "port": i+1,
                "status": state_map.get(states[i], "Other"),
                "len": lengths[i]
            })
        return res

    def start_cable_diag(self):
        """触发检测: cable_diag_get.cgi"""
        # 通常这会触发后台检测，然后需要刷新页面获取结果
        self.post_action('cable_diag_get.cgi', {})

    def get_statistics(self, port_id):
        """PortStatisticsAllRpm.htm"""
        url = f"PortStatisticsAllRpm.htm?port={port_id-1}" # 0-indexed
        html = self.get_page(url)
        rx = extract_js_variable(html, 'pkts_rx_info') or []
        tx = extract_js_variable(html, 'pkts_tx_info') or []
        return {"rx": rx, "tx": tx}
