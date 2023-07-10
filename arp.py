from netifaces import interfaces, ifaddresses, AF_INET, AF_INET6
from scapy.layers.l2 import ARP
from scapy.sendrecv import sr1
import netifaces as ni
import platform
import netifaces
import time


def get_connection_name_from_guid(iface_guids):  # 获取接口名称
    if platform.system() == "Windows":
        import winreg as wr
        # 产生接口名字清单,默认全部填写上'(unknown)'
        iface_names = ['(unknown)' for i in range(len(iface_guids))]
        # 打开"HKEY_LOCAL_MACHINE"
        reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
        # 打开r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}'
        #
        reg_key = wr.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
        for i in range(len(iface_guids)):
            try:
                # 尝试读取每一个接口ID下对应的Name
                reg_subkey = wr.OpenKey(reg_key, iface_guids[i] + r'\Connection')
                # 如果存在Name,就按照顺序写入iface_names
                iface_names[i] = wr.QueryValueEx(reg_subkey, 'Name')[0]
            except FileNotFoundError:
                pass
        # 把iface_guids, iface_names 压在一起返回
        return zip(iface_guids, iface_names)


def get_ifname(ifname):
    if platform.system() == "Linux":
        return ifname
    elif platform.system() == "Windows":
        import winreg as wr
        x = ni.interfaces()
        for i in get_connection_name_from_guid(x):
            # 找到名字所对应的接口ID并返回
            if i[1] == ifname:
                return i[0]
    else:
        print('操作系统不支持,本脚本只能工作在Windows或者Linux环境!')


def get_mac_address(ifname):  # 获取接口MAC地址
    return netifaces.ifaddresses(get_ifname(ifname))[netifaces.AF_LINK][0]['addr']


def get_ip_address(ifname):  # 获取接口ip地址
    return ifaddresses(get_ifname(ifname))[AF_INET][0]['addr']


def get_ipv6_address(ifname):  # 获取接口ipv6地址
    return ifaddresses(get_ifname(ifname))[AF_INET6][0]['addr']


def arp_request(dst, ifname):  # 构建arp请求函数
    hwsrc = get_mac_address(ifname)
    psrc = get_ip_address(ifname)
    try:
        arp_pkt = sr1(ARP(op=1, hwsrc=hwsrc, psrc=psrc, pdst=dst), timeout=5, verbose=False)
        return dst, arp_pkt.getlayer(ARP).fields['hwsrc']
    except AttributeError:
        return dst, None


if __name__ == '__main__':
    hostname = input('请输入需要请求的目的IP地址：')
    iface = input('请输入本机网卡接口名称：')
    print('正在请求', hostname, '的MAC地址，请稍等！')
    time.sleep(2)
    arp_result = arp_request(hostname, iface)
    if arp_result[1] != None:
        print('请求结果如下：')
        print('主机：', arp_result[0], 'MAC地址为：', arp_result[1])
    else:
        print('请求失败。请确保网络可达！')
