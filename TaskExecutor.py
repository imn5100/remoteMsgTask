# -*- coding=utf-8 -*-
import codecs
import hashlib
import json
import os
import subprocess
from threading import Timer

import requests

from aria2.Aria2Rpc import Aria2JsonRpc
from config import *


def md5lower(pwd):
    md5c = hashlib.md5()
    md5c.update(pwd)
    return md5c.hexdigest().lower()


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


def consumer_msg(session, topic):
    msg_response = session.get(CONSUMER_URL, params={"topic": topic})
    if msg_response:
        return json.loads(msg_response.text)
    else:
        return None


def build_py_file(data):
    if data and data['code'] == 200:
        contents = data["data"]["contents"]
        filename = "excfile/python_%s.py" % data["data"]["id"]
        exc_file = codecs.open(filename, "w", encoding='utf-8')
        exc_file.write(contents)
        exc_file.close()
        return os.path.abspath(filename)
    else:
        return None


def callback(session, id, status):
    session.get(CALLBACK_URL, params={"id": id, "type": status})


def execute_download_script(session):
    session = check_auth(session, USER_AUTH)
    data = consumer_msg(session, TOPIC["download"])
    if data and data['code'] == 200:
        try:
            url = data["data"]["contents"]
            aria2_client = Aria2JsonRpc(RPC_URL, ARIA2_PATH)
            if aria2_client.addUris([url], os.path.abspath("excfile")) == 200:
                callback(session, data["data"]["id"], STATUS_MAP["over"])
            else:
                callback(session, data["data"]["id"], STATUS_MAP["fail"])
        except Exception, e:
            print(e)
            callback(session, data["data"]["id"], STATUS_MAP["fail"])
    else:
        print("No Download Task")
        print(data)


def execute_python_script(session):
    session = check_auth(session, USER_AUTH)
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
    # 每19分钟运行一次
    Timer(1, loop_run, (execute_download_script, 60 * 1, s)).start()
    Timer(1, loop_run, (execute_python_script, 60 * 1, s)).start()
