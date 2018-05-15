# -*- coding=utf-8 -*-
import codecs
import json
import os
import subprocess
import time

from aria2.Aria2Rpc import Aria2JsonRpc
from config import DEVICE_ID, TOKEN, IS_WINDOWS, RPC_URL
from websocket import WebSocketClient

aria2_client = Aria2JsonRpc(RPC_URL)


# 传入下载url（可以是磁链）和下载保存路径，如果路径为空默认保存于excfile 文件目录下
def download_aria2(url, save_path=None):
    if not aria2_client.isAlive():
        raise Exception('*' * 10 + "Error:Please start aria2c rpc service" + '*' * 10)
    if save_path:
        aria2_client.addUris([url], save_path)
    else:
        aria2_client.addUris([url], os.path.abspath("excfile"))


# 创建python脚本文件 传入内容和编号，编号可以避免覆盖原来执行过的文件
def build_py_file(data, no):
    filename = "excfile/python_%s.py" % no
    exc_file = codecs.open(filename, "w", encoding='utf-8')
    exc_file.write(data)
    exc_file.close()
    return os.path.abspath(filename)


def message_handler(msg):
    body = msg.body
    try:
        if body.startswith('{'):
            data = json.loads(body)
            if data and data.has_key('topic'):
                if data['topic'] == 'python':
                    if data.has_key("id"):
                        filename = build_py_file(data["contents"], data["id"])
                    else:
                        filename = build_py_file(data["contents"], str(time.time()))
                    if IS_WINDOWS:
                        subprocess.call("python " + filename)
                    else:
                        os.system("python " + filename)
                    return
                elif data["topic"].lower() == "download":
                    download_aria2(data["contents"])
                    return
        print('ignore:' + str(msg))
    except Exception as e:
        print(e)
        print(msg)


if __name__ == '__main__':
    WebSocketClient.run_dolores_client(TOKEN, DEVICE_ID, message_handler=message_handler)
