# tplink_switch_manager/core.py
import requests
from urllib.parse import urljoin
from .crypto import get_encrypted_password
from .parsers import extract_tid, extract_port_num
from .constants import BASE_HEADERS
from .exceptions import LoginFailedException
from requests.adapters import HTTPAdapter


class BaseClient:
    def __init__(self, url, username, password, extra_cookies=None, timeout=10):
        self.base_url = f"{url}"
        self.username = username
        self.password = password
        self.timeout = timeout
        
        self.session = requests.Session()
        self.session.headers.update(BASE_HEADERS)
        self.session.headers.update({
            "Connection": "close"
        })
        
        # --- 新增功能：注入初始 Cookies ---
        if extra_cookies:
            self.session.cookies.update(extra_cookies)

        self.token = None
        self.max_ports = 26 

    def update_cookies(self, cookies):
        """
        运行时动态添加或更新 Cookies
        :param cookies: 字典, 如 {'custom_flag': '1'}
        """
        self.session.cookies.update(cookies)

    def login(self):
        encrypted_pwd = get_encrypted_password(self.password)
        payload = {'username': self.username, 'password': encrypted_pwd, 'logon': '登录'}
        
        try:
            # 1. Post Login
            resp = self.session.post(
                urljoin(self.base_url, 'logon.cgi'), 
                data=payload,
                timeout=self.timeout
            )
            resp.raise_for_status()
            
            # 2. Extract Token
            self.token = extract_tid(resp.text)
            if not self.token:
                idx_resp = self.session.get(
                    self.base_url,
                    timeout=self.timeout
                )

                self.token = extract_tid(idx_resp.text)
            
            if not self.token:
                raise LoginFailedException("Token not found.")
            
            # 3. Update Max Ports
            if 'max_port_num' in resp.text:
                self.max_ports = extract_port_num(resp.text)

        except Exception as e:
            raise LoginFailedException(str(e))

    def get_page(self, page):
        if not self.token: self.login()
        resp = self.session.get(
            urljoin(self.base_url, page), 
            params={'token': self.token},
            timeout=self.timeout
        )
        resp.encoding = 'utf-8'
        return resp.text

    def post_action(self, cgi, data):
        if not self.token: self.login()
        data['token'] = self.token
        resp = self.session.post(
            urljoin(self.base_url, cgi), 
            data=data,
            timeout=self.timeout
        )
        return resp