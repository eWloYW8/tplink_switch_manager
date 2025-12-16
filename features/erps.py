# tplink_switch_manager/features/erps.py
from ..parsers import extract_js_variable

class ErpsMixin:
    def get_erps_rings(self):
        """erpsGlobalRpm.htm"""
        html = self.get_page('erpsGlobalRpm.htm')
        # ringConf: [[id, mode, role, cvlan, ver, revert, ...], ...]
        rings = extract_js_variable(html, 'ringConf') or []
        res = []
        for r in rings:
            # 确保 r 是列表且长度足够
            if isinstance(r, list) and len(r) > 7:
                res.append({
                    "ring_id": r[0],
                    "mode": "Major" if r[1]==0 else "Sub",
                    "role": r[2], 
                    "control_vlan": r[3],
                    "version": r[4],
                    "revert": bool(r[5]),
                    "port0": r[6],
                    "port1": r[7]
                })
        return res

    def create_erps_ring(self, ring_id, description, cvlan, port0, port1):
        """erpsGlobalRpm.cgi"""
        data = {
            'txt_ring_id': ring_id,
            'txt_ring_des': description,
            'txt_ring_cvlan': cvlan,
            'ring_mode': 0, # Major
            'txt_ring_version': 2,
            'add_ring': 'Create'
        }
        self.post_action('erpsGlobalRpm.cgi', data)