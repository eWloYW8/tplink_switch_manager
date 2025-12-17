# tplink_switch_manager/features/erps.py
from ..parsers import extract_js_variable

class ErpsMixin:
    def get_erps_rings(self):
        html = self.get_page('erpsGlobalRpm.htm')
        rings = extract_js_variable(html, 'ringConf') or []
        res = []
        for r in rings:
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
        data = {
            'txt_ring_id': ring_id,
            'txt_ring_des': description,
            'txt_ring_cvlan': cvlan,
            'ring_mode': 0, # Major
            'txt_ring_version': 2,
            'add_ring': 'Create'
        }
        self.post_action('erpsGlobalRpm.cgi', data)

    def create_erps_instance(self, instance_id, vlan_ids):
        """
        创建 ERPS 实例
        :param instance_id: 1-8
        :param vlan_ids: 字符串 "1-10,20" 或 列表 [1, 2]
        """
        if isinstance(vlan_ids, list):
            vlan_str = ",".join(map(str, vlan_ids))
        else:
            vlan_str = str(vlan_ids)

        # GET 提交: erpsInstanceRpm.htm?instanceId=...&vlanId=...&submit=1
        params = {
            'instanceId': instance_id,
            'vlanId': vlan_str,
            'submit': 1 # 1 = Create
        }
        self.get_action('erpsInstanceRpm.htm', params)

    def delete_erps_instance(self, instance_ids):
        """
        删除 ERPS 实例
        :param instance_ids: 单个ID或ID列表
        """
        if isinstance(instance_ids, int):
            instance_ids = [instance_ids]
        
        if not instance_ids: return

        params = {'delete': 1}
        for idx, i_id in enumerate(instance_ids):
            params[f'instance{idx+1}'] = i_id
            
        self.get_action('erpsInstanceRpm.htm', params)