# -*- coding=utf-8 -*-
import codecs
import hashlib
import json
import os
import subprocess
from threading import Timer

import requests
import sys

from aria2.Aria2Rpc import Aria2JsonRpc
from config import *


# 对密码md5加密
def md5lower(pwd):
    md5c = hashlib.md5()
    md5c.update(pwd)
    return md5c.hexdigest().lower()


# 登录验证
def auth(session, user_data):
    if not session:
        session = requests.session()
    user_data["password"] = md5lower(user_data["password"])
    r = session.post(REMOTE_LOGIN_URL, user_data)
    if r.text == "200":
        return session
    else:
        print(r.text)
        return None


# 检查session是否登录通过
def check_auth(session, user_data):
    if session:
        r = session.get(CHECK_URL)
        pos = r.text.find(CHECK_STR)
        if pos > 1:
            return session
        else:
            return auth(session, user_data)
    else:
        return auth(session, user_data)


# 获得任务消息
def consumer_msg(session, topic):
    msg_response = session.get(CONSUMER_URL, params={"topic": topic})
    if msg_response:
        return json.loads(msg_response.text)
    else:
        return None


# 创建python脚本文件
def build_py_file(data):
    contents = data["data"]["contents"]
    filename = "excfile/python_%s.py" % data["data"]["id"]
    exc_file = codecs.open(filename, "w", encoding='utf-8')
    exc_file.write(contents)
    exc_file.close()
    return os.path.abspath(filename)


# 消息回调，返回任务执行状态
def callback(session, msg_id, status):
    session.get(CALLBACK_URL, params={"id": msg_id, "type": status})


# 订阅下载消息,并执行下载 （使用aria2下载）
def execute_download_script(session):
    session = check_auth(session, USER_AUTH)
    if not session:
        sys.exit(0)
    data = consumer_msg(session, TOPIC["download"])
    if data and data['code'] == 200:
        try:
            url = data["data"]["contents"]
            aria2_client = Aria2JsonRpc(RPC_URL, ARIA2_PATH)
            if aria2_client.addUris([url], os.path.abspath("excfile")):
                callback(session, data["data"]["id"], STATUS_MAP["over"])
            else:
                callback(session, data["data"]["id"], STATUS_MAP["fail"])
        except Exception, e:
            print(e)
            callback(session, data["data"]["id"], STATUS_MAP["fail"])
    else:
        print("No Download Task")
        print(data)


# 订阅python脚本消息
def execute_python_script(session):
    session = check_auth(session, USER_AUTH)
    if not session:
        sys.exit(0)
    data = consumer_msg(session, TOPIC["python"])
    if data and data['code'] == 200:
        try:
            filename = build_py_file(data)
            if filename:
                subprocess.call("python " + filename)
                callback(session, data["data"]["id"], STATUS_MAP["over"])
        except Exception, e:
            print(e)
            callback(session, data["data"]["id"], STATUS_MAP["fail"])
    else:
        print("No Python Task")
        print(data)


# 定时执行
def loop_run(fun, interval, arg, num=None):
    fun(arg)
    if num:
        # 如果限定了次数，执行次数范围内
        num -= 1
        if num > 0:
            Timer(interval, loop_run, (fun, interval, arg, num)).start()
        else:
            return
    else:
        Timer(interval, loop_run, (fun, interval, arg)).start()


if __name__ == '__main__':
    s = requests.session()
    auth(s, USER_AUTH)
    # 定时拉取消息任务  每19分钟拉取一次
    # 定时执行拉取下载任务
    Timer(1, loop_run, (execute_download_script, 60 * 19, s)).start()
    # 定时执行拉取python脚本任务
    Timer(1, loop_run, (execute_python_script, 60 * 19, s)).start()
