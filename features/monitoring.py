# tplink_switch_manager/features/monitoring.py
from ..parsers import extract_js_variable

class MonitoringMixin:
    def get_cable_diag(self):
        html = self.get_page('CableDiagRpm.htm')
        states = extract_js_variable(html, 'cablestate') or []
        lengths = extract_js_variable(html, 'cablelength') or []
        
        res = []
        state_map = {0: "No Cable", 1: "Normal", 2: "Open", 3: "Short", 4: "Open-Short", 5: "Cross"}
        length = min(len(states), len(lengths), self.max_ports)
        
        for i in range(length):
            if states[i] == -1: continue
            res.append({
                "port": i+1,
                "status": state_map.get(states[i], "Other"),
                "len": lengths[i]
            })
        return res

    def start_cable_diag(self):
        self.post_action('cable_diag_get.cgi', {})

    def get_statistics(self, port_id):
        url = f"PortStatisticsAllRpm.htm?port={port_id-1}" 
        html = self.get_page(url)
        rx = extract_js_variable(html, 'pkts_rx_info') or []
        tx = extract_js_variable(html, 'pkts_tx_info') or []
        return {"rx": rx, "tx": tx}

    def reset_poe_port(self, port_id):
        """
        重启指定 PoE 端口 (断电再上电)
        根据 MainRpm.js 的 do_submit_poe_reset 逻辑
        """
        # main_poe_port_reset.cgi (MainRpm.js 中 method="post")
        # 参数名: reset_{port_id}
        data = {
            f'reset_{port_id}': 'Re-power' # 按钮的 value 值
        }
        self.post_action('main_poe_port_reset.cgi', data)