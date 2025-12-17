# tplink_switch_manager/utils.py

def bitmap_to_ports(bitmap):
    ports = []
    current = 1
    mask = 1
    for i in range(1, 53):
        if bitmap & mask:
            ports.append(i)
        mask <<= 1
    return ports

def ports_to_bitmap(port_list):
    bitmap = 0
    for p in port_list:
        if p > 0:
            bitmap |= (1 << (p - 1))
    return bitmap