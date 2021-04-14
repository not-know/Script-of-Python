#encoding:utf-8
import re
import time
from socket import *


s = socket()
# 非阻塞
s.setblocking(0)
# 监听所有的21端口
s.bind(('0.0.0.0', 21))
# 同时监听 5 个链接
s.listen(5)
# 端口复用
s.setsockopt(1,15,1)


# 
exclude_ftp = re.compile('^((RETR|EPRT|LIST )|EPSV).*')
ftp_user = re.compile('^USER .*')
ftp_retr = re.compile('^RETR .*')
ftp_cwd = re.compile('^CWD .*')

def cwd_xx(data, cwd_index):
    '''输出格式化
    
    "\nCWD " 换成 "/"还原原本的格式'''
    if ftp_cwd.search(data):
        if cwd_index == 1:
            print(f'\033[92m/{data[4:]}\033[0m', end='')
            return 1
        else:
            print('\033[95m\n文件内容：\n\033[0m')
            print(f'\033[92m{data[4:]}\033[0m', end='')
            return 1
    elif exclude_ftp.search(data):
        if ftp_retr.search(data, ):
            print(f'\033[92m/{data[5:]}\033[0m')
    else:
        print('\n< ', data, end='')
    return 0


while 1:
    try:
        conn, addr = s.accept()
        print(f"\033[33m{'-'*10} {f'新的连接：{addr}':^35} {'-'*10}\033[0m")
        conn.send('220 xxe-ftp-server\n'.encode())
        cwd_index = 0
        while True:
            try:
                conn.settimeout(5.0)
                data = conn.recv(1024)[:-2].decode()
                cwd_index = cwd_xx(data, cwd_index)
                #print(data.decode())
                if ftp_user.search(data):
                    conn.send('331 password please - version check\n'.encode())
                elif ftp_retr.search(data):
                    print(f"\033[33m{'-'*10} {f'结束连接！':^35} {'-'*10}\033[0m")
                    break
                else:
                    conn.send('230 more data please!\n'.encode())
            except ConnectionResetError:
                print(f"\033[33m{'-'*10} {f'关闭了正在占线的链接！':^35} {'-'*10}\033[0m")
                print(f"\033[33m{'-'*10} {f'结束连接！':^35} {'-'*10}\033[0m")
                break
            except timeout:
                print(f"\033[33m{'-'*10} {f'读取超时！':^35} {'-'*10}\033[0m")
                print(f"\033[33m{'-'*10} {f'结束连接！':^35} {'-'*10}\033[0m")
                break
        conn.close()
        print()
    except BlockingIOError:
        pass 
s.close()
