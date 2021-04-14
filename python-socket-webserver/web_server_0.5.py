# -*- coding: utf-8 -*-
from socket import *
import logging
import time
import re
import os


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
            if b"\r\n\r\n" in data:
                break

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
            if len(data) <= length:
                break

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
        # 去除多余的分隔符和对上级目录
        if os.path.normpath(file_name)[:2] == "..":
            self.ser(conn, "疑似目录穿越，您访问的路径："+file_name)
        elif method == "GET":
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
        else:
            conn.sendall(
                b'HTTP/1.1 501 Method Unimplemented\r\nConnection: close\r\n\r\n')


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

    def ser(self, conn, info):
        # 危险的请求，警告
        data = "HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n兄弟别闹，你这操作很危险!!!\r\n" + info
        conn.sendall(data.encode())


class response_head:
    '''请求头部分'''

    def response_head(self):
        data = "Server: " + self.server + "\r\n\r\n"
        return data.encode()


class response_body:
    def read(self, file_name):
        if (file_name == 1) or (file_name[-1] == "/"):
            for i in self.index:
                data = self._read(file_name + i)
                if b"404" not in data[0]:
                    return data
            if self.dirlist:
                file_name = os.path.dirname(file_name)
                body = self._dirlist(file_name).encode()
                return (b"HTTP/1.1 200 OK\r\n", body)
        else:
            return self._read(file_name)

    def _read(self, file_name):
        try:
            with open(file_name) as f:
                data = f.read()
                return (b"HTTP/1.1 200 OK\r\n", data.encode())
        except PermissionError:
            return (b"HTTP/1.1 403 Forbidden\r\n", b'')
        except FileNotFoundError:
            return (b"HTTP/1.1 404 Not Found\r\n", b'')

    def format_file_size(self, filesize):
        for count in ['B', 'KB', 'MB', 'GB']:
            if filesize > -1024.0 and filesize < 1024.0:
                return f"{filesize:.2f} {count}"
            filesize /= 1024.0
        return f"{filesize} 'TB'"

    def format_time(self, mtime):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))

    def _dirlist(self, file_name):
        '''目录索引'''
        with os.scandir(file_name) as it:
            body = ''
            for i in it:
                statinfo = i.stat()
                mtime = self.format_time(statinfo.st_mtime)
                size = self.format_file_size(statinfo.st_size)
                filename = i.name
                if i.is_dir():
                    f_type = "目录"
                else:
                    f_type = "文件"
                f_path = i.path
                body += f"<tr><td valign=\"top\"><img src=\"{self.image}\" alt=\"[{f_type}]\"></td>"
                body += f"<td><a href=\"{f_path}\">{filename}</a>                     </td>"
                body += f"<td align=\"right\">{mtime}  </td><td align=\"right\">  {size} </td></tr>\r\n"

        return self.header + body + self.footer


class setting:
    '''webserver的设置'''

    # 响应头中 Server 字段
    server = "python-socket-webserver"

    # 索引页
    index = "index.html"

    # 是否开启索引目录
    dirlist = False

    # 目录索引格式
    image = "data:image/jpg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAAeAB4DASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDv7PTZPF0GlWmm3C2msmZEtZy2PKl3DY+favorwxq2vQyKNVsri41cAQ3TJcYsZWCAeYqnO09MgDGc8180fD1Z49ft7mANvtWE+4DIjCnJc/QD8yK+3NO02Ga3jBcTgqJgy8Z3Dr+tc+NWqPdwFRU4ybPkr4teCfE/jTxpE9hpkkkDuyeZHCdgAwN2fTAJrofBvgW28D6THF5aPdNw8oXDMDgnP/As/gBX07/ZawbIo5GUNxjg8d68q+LWjx6NrFrPBLxeIzPH6MpAJ/HI/EGjC1NoMwxkYzlzxPAfCVxJ4PkunuAPJuYShYdvT+dfVnwv12K88PW7Xbqt0YlPlKeAmPlAHfGcV8e6hrYbS5IXDTKY/vMACDijw58f9Q0W2t7KFHN9EPJWUgbeOMnn8cV6lfBvEQUo7pnBh6/s7xfU+4bfWYrq5ncNshiO1mbrkdh+leFeLfHFv491u4ubDc9hau1rFN2l2n5mHtkkA98ZrysfFjW9SgudLmuGkmuM+Y0jEoQeoAzgD8DTtK8Wv4cjjjZDKHQh+n3g3BHT+Egf8BFY0MDKEnJ/I6a+IhKKjFH/2Q=="
    header = f"<html>\r\n <head>\r\n  <title>目录列表</title>\r\n </head>\r\n    <meta charset=\"utf-8\">\r\n <body>\r\n<h1>目录列表</h1>\r\n  <table>\r\n   <tr><th valign=\"top\"><img src=\"{image}\" alt=\"[类型]\"></th><th><a href=\"?C=N;O=D\">文件名</a></th><th><a href=\"?C=M;O=A\">最近修改时间</a></th><th><a href=\"?C=S;O=A\">文件大小</a></th></tr>\r\n   <tr><th colspan=\"4\"><hr></th></tr>   "
    footer = "   <tr><th colspan=\"4\"><hr></th></tr>\r\n</table>\r\n</body></html>"


class web_server(request, method, setting, response_head, response_body):
    '''使用socket实现http协议的web_server

    基于socket编程实现一个简单的HTTP服务器
    服务器需要实现HEAD/GET/POST方法([CR][LF]为换行)
    对于没有实现的方法返回 501 Method Unimplemented

    属性说明：
    balabala...
    '''

    def __init__(self, ip: str, port: int, listen=5, zs=False, dkfy=True) -> None:
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
            print(
                f"\033[33m{'-'*10} {f'开 始 监 听（{self.ip}:{self.port}）':^32} {'-'*10}\033[0m\r\n")
            while True:
                try:
                    # 接收套接字
                    conn, addr = self.s.accept()
                    print(
                        f"\033[34m{'-'*10} {f'{addr} 的 连 接  ':^35} {'-'*10}\033[0m")
                    self.http(conn)
                    print(
                        f"\033[36m{'-'*10} {f'{addr} 连 接 结 束':^34} {'-'*10}\033[0m\r\n")
                except BlockingIOError as e:  # 无连接pass继续查询
                    pass
        except KeyboardInterrupt as e:
            logging.exception(e)
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
                logging.exception(e)
                conn.sendall(b'HTTP/1.1 500\r\nConnection: close\r\n\r\n')


if __name__ == "__main__":
    web = web_server("0.0.0.0", 80)
    # 必须是列表
    web.index = ["index.html"]
    web.dirlist = True
    web.start()


# 请求类：处理请求
# 响应头类：响应头部分
# 响应体类：处理文件读取
# method类：每个请求方法的处理
# 设置类： webserver的所有设置
# 继承请求和响应的webserver类：线程、资源处理

# 索引页，和 索引目录列表
# 锁目录,防止目录穿越
