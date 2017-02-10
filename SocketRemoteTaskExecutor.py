# encoding=utf-8

import codecs
import json
import os
import subprocess
import time
from socket import *
from threading import Timer

from TaskExecutor import loop_run
from aria2.Aria2Rpc import Aria2JsonRpc
from config import RPC_URL, ARIA2_PATH, APP_KEY, APP_SECRET, SERVER_ADDR

# ping 用于保持连接的心跳数据
heartbeat_data = {
    "type": "PING",
    "sessionId": ""
}
# ASK 数据请求参数类型
ask_data = {
    "type": "ASK",
    "sessionId": "",
    "contents": ""
}
# 连接认证参数
auth_data = {
    "type": "AUTH",
    "appKey": APP_KEY,
    "appSecret": APP_SECRET
}


# 创建python脚本文件 传入内容和编号，编号可以避免覆盖原来执行过的文件
def build_py_file(data, no):
    filename = "excfile/python_%s.py" % no
    exc_file = codecs.open(filename, "w", encoding='utf-8')
    exc_file.write(data)
    exc_file.close()
    return os.path.abspath(filename)


# 传入下载url（可以是磁链）和下载保存路径，如果路径为空默认保存于excfile 文件目录下
def download_aria2(url, aria2_client, save_path=None):
    if save_path:
        aria2_client.addUris([url], save_path)
    else:
        aria2_client.addUris([url], os.path.abspath("excfile"))


# 处理服务端来源的任务消息数据，需要认证appKey相同
def msg_handler(data, aria2_client):
    if data["appKey"] != APP_KEY:
        return
    if data["topic"].lower() == "python":
        if data.has_key("id"):
            filename = build_py_file(data["contents"], data["id"])
        else:
            filename = build_py_file(data["contents"], str(time.time()))
        subprocess.call("python " + filename)
    elif data["topic"].lower() == "download":
        if not aria2_client or not aria2_client.isAlive():
            aria2_client = Aria2JsonRpc(RPC_URL, ARIA2_PATH)
        download_aria2(data["contents"], aria2_client)


# 发送心跳，如果发生失败则退出程序
def send_heartbeat(client):
    try:
        client.send(json.dumps(heartbeat_data))
    except Exception as e:
        print 'heartbeat connect error : ', e
        client.close()
        exit()


# 连接发送认证数据,成功后开启心跳
def login_auth(client_sock):
    client_sock.send(json.dumps(auth_data) + "\n")
    data = client_sock.recv(8192)
    if data.lower().find("success") < 0:
        print ('Receive:' + data)
        return False
    else:
        data = json.loads(data)
        if data.has_key("success"):
            heartbeat_data["sessionId"] = data["success"]
        # 每分钟发送 心跳
        Timer(1, loop_run, (send_heartbeat, 60, client_sock)).start()
        return True


# 创建连接，验证登录成功后，设置心跳线程&阻塞等待数据
def connect_socket():
    client_sock = socket(AF_INET, SOCK_STREAM)
    aria2_client = None
    try:
        client_sock.connect(SERVER_ADDR)
    except Exception as e:
        print ('connect error : ', e)
        exit()
    try:
        if login_auth(client_sock):
            while True:
                data = client_sock.recv(8192)
                print ('Receive:' + data)
                if data is None or data == "" or data == 'quit':
                    break
                else:
                    if not data.startswith("{"):
                        continue
                    else:
                        try:
                            data = json.loads(data)
                            if data.has_key("appKey") and data.has_key("contents") and data.has_key("topic"):
                                msg_handler(data, aria2_client)
                        except Exception as e:
                            print("Execute task fail Exception:")
                            print(e)
    finally:
        client_sock.close()


if __name__ == '__main__':
    connect_socket()
