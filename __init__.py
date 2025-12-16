# tplink_switch_manager/__init__.py

from .core import BaseClient, TPLinkSwitchClient
from .exceptions import TPLinkException

__all__ = ['TPLinkSwitchClient', 'TPLinkException']