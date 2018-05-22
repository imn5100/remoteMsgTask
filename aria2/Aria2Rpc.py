# -*- coding: utf-8 -*-

import base64
import time

import requests

from config import MUST_OPEN_ARIA2C


class Aria2JsonRpc(object):
    def __init__(self, rpc_url):
        self.rpc_url = rpc_url
        if MUST_OPEN_ARIA2C and not self.isAlive():
            raise Exception("Please start aria2c rpc service")

    def execuetJsonRpcCmd(self, method, param=None):
        payload = {"jsonrpc": "2.0", "method": method, "id": 1, "params": param}
        payloads = [payload]
        tm = (time.time() * 1000)
        url = self.rpc_url % str(tm)
        print("Aria2 execute:" + str(payloads))
        r = requests.post(url, None, payloads)
        print("Aria2 back:" + r.text)
        return r.status_code == 200

    def isAlive(self):
        payload = {"jsonrpc": "2.0", "method": "aria2.tellActive", "id": 1}
        tm = (time.time() * 1000)
        url = self.rpc_url % str(tm)
        try:
            r = requests.get(url, payload)
            return r.status_code == 200
        except Exception:
            return False

    # urls 是url数组 否则传参错误 header \n分隔不同头
    def addUris(self, urls, dir=None, out=None, header=None, conn=16):
        params = []
        download_config = {}
        if dir:
            download_config["dir"] = dir
        if out:
            download_config["out"] = out
        if header:
            download_config['header'] = header
        download_config['split'] = str(conn)
        download_config['max-connection-per-server'] = str(conn)
        params.append(urls)
        params.append(download_config)
        print(self.execuetJsonRpcCmd("aria2.addUri", params))

    def addTorrent(self, path, dir=None, out=None):
        bits = open(path.decode("utf-8"), "rb").read()
        torrent = base64.b64encode(bits)
        params = []
        download_config = {"dir": dir, "out": out}
        params.append(torrent)
        params.append([])
        params.append(download_config)
        return self.execuetJsonRpcCmd("aria2.addTorrent", params)
