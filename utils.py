# tplink_switch_manager/utils.py

def bitmap_to_ports(bitmap):
    """将整数位图转换为端口列表 [1, 2, 5]"""
    ports = []
    current = 1
    mask = 1
    # 假设最大支持 52 口
    for i in range(1, 53):
        if bitmap & mask:
            ports.append(i)
        mask <<= 1
    return ports

def ports_to_bitmap(port_list):
    """将端口列表转换为整数位图"""
    bitmap = 0
    for p in port_list:
        if p > 0:
            bitmap |= (1 << (p - 1))
    return bitmap