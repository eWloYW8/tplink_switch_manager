# tplink_switch_manager/exceptions.py

class TPLinkException(Exception): pass
class LoginFailedException(TPLinkException): pass
class RequestFailedException(TPLinkException): pass
class DataParsingException(TPLinkException): pass