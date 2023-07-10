import psutil

def get_network():
    """
    获取网卡的名称, ip, mask返回格式为列表中多个元祖:类似于 [('lo', '127.0.0.1', '255.0.0.0'), ('ens33', '192.168.100.240', '255.255.255.0')]
    :return:
    """
    network_info = []
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[0] == 2 and not item[1] == '127.0.0.1':  # 不包括本地回环的话
                # if item[0] == 2:
                network_info.append((k, item[1], item[2]))
    return network_info
print(get_network())
