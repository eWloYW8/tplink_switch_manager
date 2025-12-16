from ..parsers import extract_js_variable

class SystemMixin:
    def get_system_info(self):
        html = self.get_page('MainRpm.htm')
        info = extract_js_variable(html, 'info_ds') or {}
        return {
            "desc": info.get('descriStr', [''])[0],
            "mac": info.get('macStr', [''])[0],
            "fw": info.get('firmwareStr', [''])[0],
            "hw": info.get('hardwareStr', [''])[0],
            "ip": info.get('ipStr', [''])[0],
            "uptime": info.get('workTime', [''])[0]
        }

    def set_cloud_management(self, enable=True, server_url="", port=60443):
        """配置 cloud.htm"""
        data = {
            'cloud_op': 'mngt_switch',
            'status': 1 if enable else 0,
            'cloud_type': 1, # 1=TP-LINK本地NMS
            'apply': 'Confirm'
        }
        self.post_action('cloud.cgi', data)
        
        if enable and server_url:
            tums_data = {
                'tums_server': server_url,
                'tums_port': port,
                'apply': 'Submit'
            }
            self.post_action('tumscloud.cgi', tums_data)

    def set_ip_settings(self, ip, mask, gateway, dhcp=False):
        """配置 IpSettingRpm.htm"""
        # 注意：此处有多个 Form，对应不同的 CGI
        # 设置 IP/Mask/Gateway
        data = {
            'dhcpSetting': 'enable' if dhcp else 'disable',
            'ip_address': ip,
            'ip_netmask': mask,
            'ip_gateway': gateway,
            'submit': 'Apply'
        }
        self.post_action('ip_setting.cgi', data)

    def reboot(self, save_config=True):
        self.post_action('reboot.cgi', {
            'reboot_op': 'reboot',
            'save_op': 'on' if save_config else '',
            'apply': 'Reboot'
        })

    def save_config_flash(self):
        self.post_action('savingconfig.cgi', {'action_op': 'save'})
