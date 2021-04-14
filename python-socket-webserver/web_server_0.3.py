# -*- coding: utf-8 -*-
from socket import *

class web_server:
    '''使用socket实现http协议的web_server
    
    基于socket编程实现一个简单的HTTP服务器
    服务器需要实现HEAD/GET/POST方法([CR][LF]为换行)
    对于没有实现的方法返回 501 Method Unimplemented
    
    属性说明：
    balabala...
    '''
    
    # 响应头中 Server 字段
    Server = "python-socket-webserver"
    
    def __init__(self, ip:str, port:int, listen=5, zs=False, dkfy=True) -> None:
        '''开启监听'''
        self.ip = ip
        self.port = port
        try:
            self.s = socket()
            # 非阻塞
            self.s.setblocking(zs)
            # 监听所有接口的80端口
            self.s.bind((ip, port))
            # 同时监听 5 个链接
            self.s.listen(listen)
            # 端口复用
            if dkfy:
                self.s.setsockopt(1,15,1)
        except Exception as e:
            print(f"\033[31m发生错误:\r\n{e}\033[0m")
            self.s.close()
            exit(0)
    
    def start(self):
        try:
            print(f"\033[33m{'-'*10} {f'开 始 监 听（{self.ip}:{self.port}）':^32} {'-'*10}\033[0m\r\n")
            while True:
                try:
                    # 接收套接字
                    conn, addr = self.s.accept()   
                    print(f"\033[34m{'-'*10} {f'{addr} 的 连 接  ':^35} {'-'*10}\033[0m")
                    self.http(conn)
                    print(f"\033[36m{'-'*10} {f'{addr} 连 接 结 束':^34} {'-'*10}\033[0m\r\n")
                except BlockingIOError as e: #无连接pass继续查询
                    pass
        except KeyboardInterrupt as e:
            print("\033[31m手动停止\033[0m")
            self.s.shutdown(2)
            self.s.close()
    
    def http(self, conn):
        with conn:
            try:
                # 取出请求头
                data = self.request_head(conn)
                
                # 判断请求方法，并做出响应
                self.method(conn, data)
                
                print('接收到了：')
                print(data.decode())

            except Exception as e:
                print(e)
                conn.sendall(b'HTTP/1.1 500\r\nConnection: close\r\n\r\n')
                
    def request_head(self, conn):
        '''取出请求头'''
        data = b''
        
        while True:
            _data = conn.recv(1024)
            data += _data  
            # 收到 \r\n\r\n 的时候结束接受数据
            # 先判断请求头是什么请求方法
            if b"\r\n\r\n" in data:break
            
        return data
    
    def method(self, conn, data):
        # 获取请求方法
        method = data.decode().split(' ', 1)[0]
        
        if method == "GET":
            self.get(conn, data)
        elif method == "HEAD":
            self.head(conn, data)
        elif method == "POST":
            self.post(conn, data)
        elif method == "PUT":
            self.put(conn, data)
        elif method == "DELETE":
            self.delete(conn, data)
        elif method == "OPTIONS":
            self.options(conn, data)
        elif method == "CONNECT":
            self.connect(conn, data)
        elif method == "TRACE":
            self.trace(conn, data)
        elif method == "PATCH":
            self.patch(conn, data)
        else:conn.sendall(b'HTTP/1.1 501 Method Unimplemented\r\nConnection: close\r\n\r\n')
            
    def get(self, conn, data):
        # 返回响应
        conn.sendall(b"HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n")
    
    def head(self, conn, data):
        # 返回响应
        conn.sendall(b"HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n")
    
    def post(self, conn, data):
        # 返回响应
        conn.sendall("HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n方法还没有实现马上就好".encode())
    
    def put(self, conn, data):
        # 返回响应
        conn.sendall("HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n方法还没有实现马上就好".encode())
        
    def delete(self, conn, data):
        # 返回响应
        conn.sendall("HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n方法还没有实现马上就好".encode())
        
    def options(self, conn, data):
        # 返回响应
        conn.sendall("HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n方法还没有实现马上就好".encode())
        
    def connect(self, conn, data):
        # 返回响应
        conn.sendall("HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n方法还没有实现马上就好".encode())
        
    def trace(self, conn, data):
        # 返回响应
        conn.sendall("HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n方法还没有实现马上就好".encode())

    def patch(self, conn, data):
        # 返回响应
        conn.sendall("HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n方法还没有实现马上就好".encode())


if __name__ == "__main__":
    web = web_server("0.0.0.0", 80)
    web.start()



# 请求类：处理请求
# 响应头类：响应头部分
# 响应体类：处理文件读取
# 继承请求和响应的webserver类：线程、资源处理
