# -*- coding=utf-8 -*-
from aria2.Aria2Rpc import Aria2JsonRpc
from config import RPC_URL

headers = {
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'wst.shawblog.me',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'text/plain, */*; q=0.01',
    'Connection': 'keep-alive',
}


def test_aria2_add_url():
    rpc = Aria2JsonRpc(RPC_URL)
    headers['Cookie'] = "sessionId=sadsadsad;uind=asdas1212das"
    rpc.addUris(['http://localhost:9010/login'], headers=headers)


if __name__ == '__main__':
    test_aria2_add_url()
