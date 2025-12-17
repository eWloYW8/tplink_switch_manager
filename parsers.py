# tplink_switch_manager/parsers.py
import re
import chompjs
from .exceptions import DataParsingException

def extract_js_variable(html_content, var_name):
    if not html_content:
        return None

    pattern = re.compile(
        r'var\s+' + re.escape(var_name) + r'\s*=\s*(.*?);', 
        re.DOTALL | re.IGNORECASE
    )
    
    match = pattern.search(html_content)
    
    if match:
        raw_js_obj = match.group(1).strip()
        
        if raw_js_obj.lower().startswith('new array'):
            start_idx = raw_js_obj.find('(')
            end_idx = raw_js_obj.rfind(')')
            
            if start_idx != -1 and end_idx != -1:
                content = raw_js_obj[start_idx+1:end_idx]
                raw_js_obj = f"[{content}]"

        try:
            return chompjs.parse_js_object(raw_js_obj)
        except ValueError as e:
            print(f"Warning: chompjs failed to parse {var_name}: {e}")
            return None
    
    return None

def extract_tid(html_content):
    if not html_content: return None
    
    pattern = re.compile(r'var\s+g_tid\s*=\s*["\']?(\d+)["\']?')
    match = pattern.search(html_content)
    
    if match:
        return match.group(1)

    pattern_comma = re.compile(r'g_tid\s*=\s*["\']?(\d+)["\']?')
    match_comma = pattern_comma.search(html_content)
    if match_comma:
        return match_comma.group(1)
        
    return None
