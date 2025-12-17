# tplink_switch_manager/features/system.py
from ..parsers import extract_js_variable
from ..crypto import get_encrypted_password

class SystemMixin:
    def get_system_info(self):
        html = self.get_page('MainRpm.htm')
        info = extract_js_variable(html, 'info_ds') or {}
        
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
            'save_op': 'true' if save_config else 'false',
            'apply': 'Reboot'
        })

    def save_config_flash(self):
        self.post_action('savingconfig.cgi', {'action_op': 'save'})

    def factory_reset(self):
        # SystemResetRpm.htm: <form name=reset_fm action=reset.cgi method=post>
        self.post_action('reset.cgi', {
            'reset_op': 'factory',
            'apply': 'Reset'
        })

    def set_ip_settings(self, ip, mask, gateway, manage_vlan=1, dhcp=False):
        # IpSettingRpm.htm: <form name=ip_setting action=ip_setting.cgi>
        data = {
            'manage_vlan': manage_vlan,
            'dhcpSetting': 'enable' if dhcp else 'disable',
            'ip_address': ip,
            'ip_netmask': mask,
            'ip_gateway': gateway,
            'submit': 'Apply'
        }
        self.get_action('ip_setting.cgi', data)

    def set_user_account(self, username, old_password, new_password):
        enc_old = get_encrypted_password(old_password)
        enc_new = get_encrypted_password(new_password)
        enc_confirm = get_encrypted_password(new_password)

        # UserAccountRpm.htm: <form name=usr_account_setting action=usr_account_set.cgi ...>
        data = {
            'txt_username': username,
            'txt_oldpwd': enc_old,
            'txt_userpwd': enc_new,
            'txt_confirmpwd': enc_confirm,
            'apply': 'Apply'
        }
        self.get_action('usr_account_set.cgi', data)