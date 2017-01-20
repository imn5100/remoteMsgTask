# encoding=utf-8

import codecs
import json
import subprocess
import time
import os
from socket import *

from aria2.Aria2Rpc import Aria2JsonRpc
from config import RPC_URL, ARIA2_PATH, APP_KEY, APP_SECRET, SERVER_ADDR


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


def connect_socket():
    BUFSIZE = 8192
    clientSock = socket(AF_INET, SOCK_STREAM)
    try:
        clientSock.connect(SERVER_ADDR)
    except Exception as e:
        print 'connect error : ', e
        sys.exit()
    # 构建连接认证参数
    auth_data = {
        "type": 1,
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    clientSock.send(json.dumps(auth_data) + "\n")
    data = clientSock.recv(BUFSIZE)
    aria2_client = None
    # 第一次连接发送认证数据,返回数据非成功则关闭连接
    if data.lower() != "success":
        print ('recieve:' + data)
    else:
        # 否则阻塞服务器数据
        while True:
            # 阻塞到收到消息
            data = clientSock.recv(BUFSIZE)
            # 服务端关闭连接时会发送一个空字符串
            if data == "":
                # When the remote end is closed and all data is read, return the empty string.
                break
            else:
                print ('recieve:' + data)
                # 非json字符输出后无视
                if not data.startswith("{"):
                    continue
                try:
                    # 转化json数据
                    # {"appkey":"*","contents":"http://shawblog.me","createTime":1484621268635,"id":14,"opTime":1484621268635,"status":1,"topic":"Download"}
                    if data:
                        data = json.loads(data)
                        # 判断传来的数据是否是有必须参数
                        if data.has_key("appkey") and data.has_key("contents") and data.has_key("topic"):
                            if data["appkey"] != APP_KEY:
                                # appkey不一致的消息不处理
                                continue
                            if data["topic"].lower() == "python":
                                if data.has_key("id"):
                                    filename = build_py_file(data["contents"], data["id"])
                                else:
                                    filename = build_py_file(data["contents"], str(time.time()))
                                subprocess.call("python " + filename)
                            elif data["topic"].lower() == "download":
                                try:
                                    if not aria2_client or not aria2_client.isAlive():
                                        aria2_client = Aria2JsonRpc(RPC_URL, ARIA2_PATH)
                                    download_aria2(data["contents"], aria2_client)
                                except:
                                    print("Download Error Please check the aria2 is open")
                                    break
                except Exception as e:
                    print("Execute task fail Exception:")
                    print(e)
    clientSock.close()


if __name__ == '__main__':
    connect_socket()
