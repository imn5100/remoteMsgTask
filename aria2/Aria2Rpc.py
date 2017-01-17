# -*- coding: utf-8 -*-
import requests
import os
import time
import base64


class Aria2JsonRpc(object):
    def __init__(self, rpc_url, arai2_path):
        self.rpc_url = rpc_url
        self.arai2_path = arai2_path
        if not self.isAlive():
            self.startAria2Rpc()

    def startAria2Rpc(self):
        launch_file = open("startAria2Rpc.bat", "w")
        new_cmd = "\"" + self.arai2_path + "aria2c.exe\"  --enable-rpc --rpc-listen-all=true --rpc-allow-origin-all -c"
        launch_file.write(new_cmd)
        launch_file.close()
        # aria2 使用cmd打开
        os.startfile((os.getcwd() + "\\startAria2Rpc.bat"))
        # 进程挂起3秒保证aria2打开完毕
        time.sleep(3)

    def execuetJsonRpcCmd(self, method, param=None):
        payload = {"jsonrpc": "2.0", "method": method, "id": 1, "params": param}
        payloads = [payload]
        tm = long(time.time() * 1000)
        url = self.rpc_url % str(tm)
        print("Aria2 execute:" + str(payloads))
        r = requests.post(url, None, payloads)
        print("Aria2 back:" + r.text)
        return r.status_code == 200

    def isAlive(self):
        payload = {"jsonrpc": "2.0", "method": "aria2.tellActive", "id": 1}
        tm = long(time.time() * 1000)
        url = self.rpc_url % str(tm)
        try:
            r = requests.get(url, payload)
            return r.status_code == 200
        except Exception:
            return False

    # urls 是url数组 否则传参错误
    def addUris(self, urls, dir=None, out=None):
        params = []
        download_config = {}
        if dir:
            download_config["dir"] = dir
        if out:
            download_config["out"] = out
        params.append(urls)
        params.append(download_config)
        return self.execuetJsonRpcCmd("aria2.addUri", params)

    def addTorrent(self, path, dir=None, out=None):
        bits = open(path.decode("utf-8"), "rb").read()
        torrent = base64.b64encode(bits)
        params = []
        download_config = {"dir": dir, "out": out}
        params.append(torrent)
        params.append([])
        params.append(download_config)
        return self.execuetJsonRpcCmd("aria2.addTorrent", params)
