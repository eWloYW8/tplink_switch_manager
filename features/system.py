# tplink_switch_manager/features/system.py
from ..parsers import extract_js_variable

class SystemMixin:
    def get_system_info(self):
        html = self.get_page('MainRpm.htm')
        info = extract_js_variable(html, 'info_ds') or {}
        
        # 辅助函数，安全获取列表第一项
        def get_first(key):
            val = info.get(key)
            if isinstance(val, list) and len(val) > 0:
                return val[0]
            return ""

        return {
            "desc": get_first('descriStr'),
            "mac": get_first('macStr'),
            "fw": get_first('firmwareStr'),
            "hw": get_first('hardwareStr'),
            "ip": get_first('ipStr'),
            "uptime": get_first('workTime')
        }

    def reboot(self, save_config=True):
        self.post_action('reboot.cgi', {
            'reboot_op': 'reboot',
            'save_op': 'true' if save_config else 'false', # 修正此处
            'apply': 'Reboot'
        })

    def save_config_flash(self):
        self.post_action('savingconfig.cgi', {'action_op': 'save'})