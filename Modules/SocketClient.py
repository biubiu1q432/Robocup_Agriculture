# -*- coding:utf-8 -*-
import time
import socket
import threading as th

'''
    基本没用到这个网络通信，只是用来告知另一辆车已经抓完了而已
'''

class SocketClient:
    def __init__(self, remote_ip=('192.168.90.164', 6666)):
        self.start_or_end = 1   # 1表示start，2表示end
        self.arrive_end = 0     # 如果到了终点，go_end会改这里的

        self.REMOTE_IP = remote_ip
        self.BUFFER_SIZE = 1024
        self.SOCKET_TIMEOUT_TIME = 60


        self.msg_start = 'start'
        self.msg_end = 'end'

    def send_socket_info(self, handle, msg, side='server', do_encode=True, do_print_info=True):
        """
        发送socket info，并根据side打印不同的前缀信息
        :param handle: socket句柄
        :param msg: 要发送的内容
        :param side: 默认server端
        :param do_encode: 是否需要encode，默认True
        :param do_print_info: 是否需要打印socket信息，默认True
        :return:
        """
        if do_encode:
            handle.send(msg.encode())
        else:
            handle.send(msg)

        if do_print_info:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            if side == 'server':
                print(f'Server send --> {current_time} - {msg}')
            else:
                print(f'Client send --> {current_time} - {msg}')
    
    def receive_socket_info(self, handle, expected_msg, side='server', do_decode=True, do_print_info=True):
        """
        循环接收socket info，判断其返回值，直到指定的值出现为止，防止socket信息粘连，并根据side打印不同的前缀信息
        :param handle: socket句柄
        :param expected_msg: 期待接受的内容，如果接受内容不在返回结果中，一直循环等待，期待内容可以为字符串，也可以为多个字符串组成的列表或元组
        :param side: 默认server端
        :param do_decode: 是否需要decode，默认True
        :param do_print_info: 是否需要打印socket信息，默认True
        :return:
        """
        while True:
            if do_decode:
                socket_data = handle.recv(self.BUFFER_SIZE).decode()
            else:
                socket_data = handle.recv(self.BUFFER_SIZE)

            if do_print_info:
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                if side == 'server':
                    print(f'Server received ==> {current_time} - {socket_data}')
                else:
                    print(f'Client received ==> {current_time} - {socket_data}')

            # 如果expected_msg为空，跳出循环
            if not expected_msg:
                break

            if isinstance(expected_msg, (list, tuple)):
                flag = False
                for expect in expected_msg:  # 循环判断每个期待字符是否在返回结果中
                    if expect in socket_data:  # 如果有任意一个存在，跳出循环
                        flag = True
                        break
                if flag:
                    break
            else:
                if expected_msg in socket_data:
                    break
            time.sleep(1)  # 每隔1秒接收一次socket
        return socket_data
    
    def start_client_socket(self):
        """
        启动客户端TCP Socket
        :return:
        """
        ip, port = self.REMOTE_IP
        client = socket.socket()  # 使用TCP方式传输
        print(f'开始连接服务端 {ip}:{port} ...')
        client.connect((ip, port))  # 连接远程服务端
        print(f'连接服务端 {ip}:{port} 成功')
        client.settimeout(self.SOCKET_TIMEOUT_TIME)  # 设置客户端超时时间

        # 与服务端握手，达成一致
        self.send_socket_info(handle=client, side='client', msg='客户端已就绪')
        self.receive_socket_info(handle=client, side='client', expected_msg='服务端已就绪')

        # 与服务端交互
        while self.start_or_end == 1:
            answer = self.msg_start
            self.send_socket_info(handle=client, side='client', msg=answer)
            socket_data = self.receive_socket_info(handle=client, side='client', expected_msg='')
            if 'quit' in socket_data:
                print('大车已启动')
                self.start_or_end = 2
                break

        while self.start_or_end == 2 and not self.arrive_end:
            time.sleep(0.2)
        
        try:
            answer = self.msg_end
            self.send_socket_info(handle=client, side='client', msg=answer)
            if 'quit' in socket_data:
                print('成功发送end')
            print('socket结束')
        except:
            print('error: 因为某些原因没能把end发过去')

            
        # 断开socket连接
        client.close()
        print(f'与服务端 {ip}:{port} 断开连接')


    def run_thread(self):
        thread = th.Thread(target=self.start_client_socket)
        thread.start()