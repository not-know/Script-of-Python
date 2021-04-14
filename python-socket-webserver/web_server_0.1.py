# -*- coding: utf-8 -*-
# 失败原因：因为没办法确定接受多少数据，导致recv一直等待接受数据，最后超时
from socket import *

def http_server(conn, addr):

    with conn:
        try:
            # 接受的数据
            data = b''

            while True:
                _data = conn.recv(1024)
                
                data += _data
                
                # 没有数据时结束循环
                if not _data:break
                
            print('接收到了：')
            print(data.decode())

            conn.sendall(b"HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n")
            
        except Exception as e:
            print(e)
            conn.sendall(b'HTTP/1.1 500\r\nConnection: close\r\n\r\n')

if __name__ == "__main__":

    with socket() as s:

        # 非阻塞
        s.setblocking(0)
        # 监听所有接口的80端口
        s.bind(('0.0.0.0', 80))
        # 同时监听 5 个链接
        s.listen(5)
        # 端口复用
        s.setsockopt(1,15,1)

        print(f"\033[33m{'-'*10} {'开 始 监 听':^35} {'-'*10}\033[0m\r\n")
        
        while True:
            try:
                # 接收套接字
                conn, addr = s.accept()   
                print(f"\033[34m{'-'*10} {f'{addr} 的连接':^35} {'-'*10}\033[0m")
                http_server(conn, addr)
                print(f"\033[36m{'-'*10} {'连 接 结 束':^35} {'-'*10}\033[0m\r\n")
            except Exception as e: #无连接pass继续查询
                pass