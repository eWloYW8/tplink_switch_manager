# tplink_switch_manager/parsers.py
import re
import chompjs  # 使用专门的 JS 解析库
from .exceptions import DataParsingException

def extract_js_variable(html_content, var_name):
    """
    使用 chompjs 提取并解析 HTML 中的 JS 变量。
    能完美处理嵌套对象、十六进制数值、注释和无引号键名。
    同时兼容 new Array() 语法。
    """
    if not html_content:
        return None

    # 1. 定位变量定义
    # 匹配模式: var var_name = ... ;
    # 使用非贪婪匹配找到分号结尾
    pattern = re.compile(
        r'var\s+' + re.escape(var_name) + r'\s*=\s*(.*?);', 
        re.DOTALL | re.IGNORECASE
    )
    
    match = pattern.search(html_content)
    
    if match:
        raw_js_obj = match.group(1).strip()
        
        # --- 修复逻辑开始 ---
        # 处理 TP-Link 特有的 new Array() 语法
        # 例如: var bcInfo = new Array(\n0,0,0,\n...);
        if raw_js_obj.lower().startswith('new array'):
            # 查找第一个 '(' 和最后一个 ')'
            start_idx = raw_js_obj.find('(')
            end_idx = raw_js_obj.rfind(')')
            
            if start_idx != -1 and end_idx != -1:
                # 提取括号内的内容
                content = raw_js_obj[start_idx+1:end_idx]
                # 替换为列表字面量格式
                raw_js_obj = f"[{content}]"
        # --- 修复逻辑结束 ---

        try:
            # chompjs 可以处理换行符、尾部逗号和十六进制
            return chompjs.parse_js_object(raw_js_obj)
        except ValueError as e:
            print(f"Warning: chompjs failed to parse {var_name}: {e}")
            return None
    
    return None

def extract_tid(html_content):
    """
    从 index.html 或 MainRpm.htm 中提取全局 Token ID (g_tid)
    """
    if not html_content: return None
    
    # 匹配: var g_tid=2123408165; 或 g_tid = "..."
    # chompjs 也可以用，但这里简单的正则通常足够且更快
    pattern = re.compile(r'var\s+g_tid\s*=\s*["\']?(\d+)["\']?')
    match = pattern.search(html_content)
    
    if match:
        return match.group(1)
        
    # 备用匹配: g_tid在逗号分隔的列表中
    # var g_Lan=0, ... ,g_tid=2123408165;
    pattern_comma = re.compile(r'g_tid\s*=\s*["\']?(\d+)["\']?')
    match_comma = pattern_comma.search(html_content)
    if match_comma:
        return match_comma.group(1)
        
    return None

def extract_port_num(html_content):
    if not html_content: return 26
    
    # 尝试提取 max_port_num
    val = extract_js_variable(html_content, 'max_port_num')
    if val is not None and isinstance(val, int):
        return val
        
    return 26