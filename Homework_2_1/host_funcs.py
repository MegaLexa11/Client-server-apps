import platform
from tabulate import tabulate
from ipaddress import ip_address
from subprocess import Popen, PIPE


def host_ping(address_list):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    send_times = '1'  # Для ускорения работы
    result_list = ([], [])
    for address in address_list:
        args = ['ping', param, send_times, address]
        reply = Popen(args, stdout=PIPE, stderr=PIPE)
        code = reply.wait()
        if code == 0:
            print(f'{address}: access available.')
            result_list[0].append(address)
        else:
            print(f'{address}: access denied.')
            result_list[1].append(address)
    return result_list


def host_range_ping(from_ip, to_ip):
    try:
        ip_addresses = []
        ip_1 = ip_address(from_ip)
        ip_2 = ip_address(to_ip)
        if ip_2 < ip_1:
            ip_1, ip_2 = ip_2, ip_1
        while ip_1 <= ip_2:
            ip_addresses.append(str(ip_1))
            ip_1 += 1
        return host_ping(ip_addresses)
    except ValueError:
        print('Incorrect data!!!')


def host_range_ping_tab(from_ip, to_ip):
    ip_reachable, ip_unreachable = host_range_ping(from_ip, to_ip)
    counter = max(len(ip_reachable), len(ip_unreachable))
    ip_tab = []
    for ind in range(counter):
        try:
            ip_r = ip_reachable[ind]
        except IndexError:
            ip_r = ''
        try:
            ip_u = ip_unreachable[ind]
        except IndexError:
            ip_u = ''
        ip_tab.append((ip_r, ip_u))
    tab_headers = ['reachable', 'unreachable']
    print('Summary:')
    print(tabulate(ip_tab, headers=tab_headers, tablefmt='grid'))


if __name__ == '__main__':
    addresses = ['google.com', '127.0.0.8', 'some_connection']
    addr_1 = '127.0.0.8'
    addr_2 = '127.0.0.1'
    # host_ping(addresses)
    # host_range_ping(addr_1, addr_2)
    host_range_ping_tab(addr_1, addr_2)
