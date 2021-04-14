# -*- coding: utf-8 -*-
from socket import *
import re

class request:
    '''对请求作出处理
    
    识别请求方法，和接受数据的大小
    '''

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

    def request_body(self, conn, data):
        '''提取请求体'''

        # 提取 Content-Length 的值，也就是请求体的长度
        length = re.search(r'Content-Length:\s*(\d*)', data).group(1)

        # 提取出请求体，之前接受数据可能会多接收。
        index = data.index(b'\r\n\r\n') + 4
        data = data[index:]

        # 接收数据
        while True:
            _data = conn.recv(1024)
            data += _data  
            # 接收到指定长度后结束循环
            if len(data) <= length:break
        
        return data

    def method(self, conn, data):
        # 以空格切割data,提取出第一行
        data_head = data.decode().split(' ', 3)[:-1]
        # 提取请求方法
        method = data_head[0]
        # 提取文件路径
        file_name = "./" + data_head[1]
        # 判断有没有问号（？），并删掉问号后面的字符
        if "?" in file_name:
            index = file_name.index("?") 
            file_name = file_name[:index] 

        if method == "GET":
            self.get(conn, data, file_name)
        elif method == "HEAD":
            self.head(conn, data, file_name)
        elif method == "POST":
            self.post(conn, data, file_name)
        elif method == "PUT":
            self.put(conn, data, file_name)
        elif method == "DELETE":
            self.delete(conn, data, file_name)
        elif method == "OPTIONS":
            self.options(conn, data, file_name)
        elif method == "CONNECT":
            self.connect(conn, data, file_name)
        elif method == "TRACE":
            self.trace(conn, data, file_name)
        elif method == "PATCH":
            self.patch(conn, data, file_name)
        else:conn.sendall(b'HTTP/1.1 501 Method Unimplemented\r\nConnection: close\r\n\r\n')
   

class response_head:
    '''请求头部分'''

    # 响应头中 Server 字段
    Server = "python-socket-webserver"
    
    def response_head(self):
        data = "Server: " + self.Server + "\r\n\r\n"
        return data.encode()

class response_body:
    def read(self, file_name):
        try:
            with open(file_name) as f:
                data = f.read()
                return (b"HTTP/1.1 200 OK\r\n", data.encode())
        except PermissionError:
            return (b"HTTP/1.1 403 Forbidden\r\n", b'')
        except FileNotFoundError:
            return (b"HTTP/1.1 404 Not Found\r\n", b'')
        

class method:
    '''请求方法'''

    TEST = "HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n方法还没有实现马上就好".encode()

    def get(self, conn, data, file_name):
        # 返回响应
        status, body = self.read(file_name)
        length = "Content-Length: " + str(len(body)) + "\r\n"
        length = length.encode()
        response = status + length + self.response_head() + body
        conn.sendall(response)
    
    def head(self, conn, data, file_name):
        # 返回响应
        status, body = self.read(file_name)
        response = status + self.response_head()
        conn.sendall(response)
    
    def post(self, conn, data, file_name):
        # 返回响应
        conn.sendall(self.TEST)
    
    def put(self, conn, data, file_name):
        # 返回响应
        conn.sendall(self.TEST)
        
    def delete(self, conn, data, file_name):
        # 返回响应
        conn.sendall(self.TEST)
        
    def options(self, conn, data, file_name):
        # 返回响应
        conn.sendall(self.TEST)
        
    def connect(self, conn, data, file_name):
        # 返回响应
        conn.sendall(self.TEST)
        
    def trace(self, conn, data, file_name):
        # 返回响应
        conn.sendall(self.TEST)

    def patch(self, conn, data, file_name):
        # 返回响应
        conn.sendall(self.TEST)


class web_server(request, method, response_head, response_body):
    '''使用socket实现http协议的web_server
    
    基于socket编程实现一个简单的HTTP服务器
    服务器需要实现HEAD/GET/POST方法([CR][LF]为换行)
    对于没有实现的方法返回 501 Method Unimplemented
    
    属性说明：
    balabala...
    '''
    
    def __init__(self, ip:str, port:int, listen=5, zs=False, dkfy=True) -> None:
        '''开启监听'''
        self.ip = ip
        self.port = port
        
        self.s = socket()
        # 端口复用
        if dkfy:
            self.s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # 非阻塞
        self.s.setblocking(zs)
        # 监听所有接口的80端口
        self.s.bind((ip, port))
        # 同时监听 5 个链接
        self.s.listen(listen)
    
    def start(self):
        '''开启服务，线程控制'''
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
                

if __name__ == "__main__":
    web = web_server("0.0.0.0", 80)   
    web.start()



# 请求类：处理请求
# 响应头类：响应头部分
# 响应体类：处理文件读取
# method类：每个请求方法的处理
# 继承请求和响应的webserver类：线程、资源处理
