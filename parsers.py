import re
import ast
from .exceptions import DataParsingException

def extract_js_variable(html_content, var_name):
    """
    提取 HTML 中的 JS 变量，支持 Object {}, Array [], 和 new Array()
    """
    # 1. 尝试匹配 new Array(...) 语法 (常见于旧版 TPLink固件)
    # 匹配: var bcInfo = new Array(\n0,0,0...);
    pattern_new_array = re.compile(
        r'var\s+' + re.escape(var_name) + r'\s*=\s*new\s+Array\((.*?)\)', 
        re.DOTALL | re.IGNORECASE
    )
    match_new_array = pattern_new_array.search(html_content)
    
    if match_new_array:
        raw_content = match_new_array.group(1)
        # 将 JS 的 new Array(1,2,3) 内容包裹为 Python 列表 [1,2,3]
        try:
            # Python 的 eval 可以处理数字列表、换行符和尾部逗号
            return eval(f"[{raw_content}]")
        except Exception as e:
            print(f"Warning: Failed to parse new Array content for {var_name}: {e}")
            return []

    # 2. 尝试匹配标准字面量 {...} 或 [...]
    # 这里的正则使用了非贪婪匹配，并增加 lookahead 确保匹配完整
    pattern_literal = re.compile(
        r'var\s+' + re.escape(var_name) + r'\s*=\s*({.*?}|\[.*?\])(?=\s*;|\s+var|\s*<|\s*$)', 
        re.DOTALL
    )
    
    match_literal = pattern_literal.search(html_content)
    # 如果 lookahead 失败，尝试简单的非贪婪匹配作为回退
    if not match_literal:
        pattern_literal_fallback = re.compile(
            r'var\s+' + re.escape(var_name) + r'\s*=\s*({.*?}|\[.*?\])', 
            re.DOTALL
        )
        match_literal = pattern_literal_fallback.search(html_content)

    if match_literal:
        raw_js = match_literal.group(1)
        # 预处理：给未加引号的键加引号 (key: -> "key":)
        raw_js = re.sub(r'([a-zA-Z0-9_]+)\s*:', r'"\1":', raw_js)
        # 预处理：保留十六进制 0x...
        raw_js = re.sub(r'0x([0-9a-fA-F]+)', r'0x\1', raw_js) 
        
        try:
            return eval(raw_js) 
        except Exception as e:
            print(f"Warning: Failed to parse literal for {var_name}: {e}")
            return None

    return None

def extract_tid(html_content):
    """
    Extracts the global Token ID (g_tid) from index.html or other pages.
    Compatible with:
    1. var g_tid=2123408165;
    2. var g_Lan=0,...,g_tid=2123408165;
    """
    pattern = re.compile(r'g_tid\s*=\s*["\']?(\d+)["\']?')
    match = pattern.search(html_content)
    
    if match:
        return match.group(1)
    return None

def extract_port_num(html_content):
    pattern = re.compile(r'max_port_num\s*=\s*(\d+)')
    match = pattern.search(html_content)
    return int(match.group(1)) if match else 26
