# tplink_switch_manager/__init__.py

from .core import BaseClient
from .features.system import SystemMixin
from .features.switching import SwitchingMixin
from .features.vlan import VlanMixin
from .features.qos import QosMixin
from .features.security import SecurityMixin
from .features.monitoring import MonitoringMixin
from .features.erps import ErpsMixin
from .exceptions import TPLinkException

class TPLinkSwitchClient(BaseClient, SystemMixin, SwitchingMixin, VlanMixin, 
                         QosMixin, SecurityMixin, MonitoringMixin, ErpsMixin):
    """
    全功能 TP-Link 交换机管理客户端
    """
    def __init__(self, ip, username, password, extra_cookies=None, timeout=10):
        super().__init__(ip, username, password, extra_cookies, timeout)

__all__ = ['TPLinkSwitchClient', 'TPLinkException']