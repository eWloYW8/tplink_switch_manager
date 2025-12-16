# tplink_switch_manager/core.py
import requests
from urllib.parse import urljoin
from .crypto import get_encrypted_password
from .parsers import extract_tid, extract_port_num
from .constants import BASE_HEADERS
from .exceptions import LoginFailedException
from .features.system import SystemMixin
from .features.switching import SwitchingMixin
from .features.vlan import VlanMixin
from .features.qos import QosMixin
from .features.security import SecurityMixin
from .features.monitoring import MonitoringMixin
from .features.erps import ErpsMixin

class BaseClient:
    def __init__(self, url, username, password, extra_cookies=None, timeout=10):
        self.base_url = url if url.endswith('/') else url + '/'
        self.username = username
        self.password = password
        self.timeout = timeout
        
        self.session = requests.Session()
        self.session.headers.update(BASE_HEADERS)
        # 关键修正：TP-Link CGI 严格检查 Referer
        self.session.headers.update({
            "Referer": self.base_url,
            "Connection": "keep-alive"
        })
        
        if extra_cookies:
            self.session.cookies.update(extra_cookies)

        self.token = None
        self.max_ports = 26 

    def login(self):
        encrypted_pwd = get_encrypted_password(self.password)
        payload = {
            'username': self.username, 
            'password': encrypted_pwd, 
            'logon': 'Login'
        }
        
        try:
            # 1. Post Login
            # 注意：logon.cgi 通常返回一段 JS 重定向，而不是直接包含 Token
            login_url = urljoin(self.base_url, 'logon.cgi')
            resp = self.session.post(
                login_url, 
                data=payload,
                timeout=self.timeout
            )
            resp.raise_for_status()
            
            # 2. Extract Token form Index
            # 登录成功后，必须访问主页 (index.html 或 MainRpm.htm) 才能拿到 g_tid
            index_resp = self.session.get(
                self.base_url,
                timeout=self.timeout
            )
            index_resp.encoding = 'utf-8' # 强制 utf-8 防止乱码

            self.token = extract_tid(index_resp.text)
            
            if not self.token:
                # 尝试备用页面
                main_resp = self.session.get(
                    urljoin(self.base_url, 'MainRpm.htm'),
                    timeout=self.timeout
                )
                self.token = extract_tid(main_resp.text)

            if not self.token:
                raise LoginFailedException("Login successful but Token (g_tid) not found.")
            
            # 3. Get Port Num (可选，从 CableDiagRpm 或 MainRpm 获取)
            # 为了准确，我们可以请求一次 CableDiagRpm.htm
            diag_resp = self.get_page_raw('CableDiagRpm.htm')
            if diag_resp:
                self.max_ports = extract_port_num(diag_resp)

        except Exception as e:
            raise LoginFailedException(f"Connection failed: {str(e)}")

    def get_page_raw(self, page):
        """内部方法：获取页面内容，带 Token"""
        if not self.token: self.login()
        try:
            resp = self.session.get(
                urljoin(self.base_url, page), 
                params={'token': self.token},
                timeout=self.timeout
            )
            resp.encoding = 'utf-8'
            return resp.text
        except Exception:
            return None

    def get_page(self, page):
        """公开方法：获取页面内容"""
        text = self.get_page_raw(page)
        if text is None:
            raise requests.RequestException(f"Failed to get page {page}")
        return text

    def post_action(self, cgi, data):
        if not self.token: self.login()
        
        post_url = urljoin(self.base_url, cgi)
        params = {'token': self.token}
        
        # Body 中也加入 token
        data['token'] = self.token
        
        resp = self.session.post(
            post_url, 
            params=params,
            data=data,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp

    def get_action(self, cgi, params):
        if not self.token: self.login()

        url = urljoin(self.base_url, cgi)
        params['token'] = self.token

        resp = self.session.get(
            url, 
            params=params,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp

class TPLinkSwitchClient(BaseClient, SystemMixin, SwitchingMixin, VlanMixin, 
                         QosMixin, SecurityMixin, MonitoringMixin, ErpsMixin):
    """
    全功能 TP-Link 交换机管理客户端
    """
    pass