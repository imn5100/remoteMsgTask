# encoding=utf-8

#
# echo程序客户端，服务端把每条消息打上时间戳后返回
#
import json
from socket import *

import redis


def test_socket():
    BUFSIZE = 8192
    serverAddr = ('139.196.45.8', 8001)
    clientSock = socket(AF_INET, SOCK_STREAM)

    try:
        clientSock.connect(serverAddr)  # 若要连接的服务端没有启动，这里会抛出异常
    except Exception as e:  # 不知道这里捕获什么具体的异常了，就用的一个比较基层的类Exception
        print 'exception catched : ', e
        sys.exit()
    data = {"type": 1}
    # data["appkey"] = raw_input('input auth appkey :')
    # if not data:  # 直接回车就没有输入内容,退出
    #     print 'client quit'
    #     clientSock.close()  # 要close一下
    clientSock.send(
            '{"appkey": "*", "type": 1,"appSecret":"*","unused":"中文测试"}' + "\n")
    while True:
        # 阻塞到收到消息
        data = clientSock.recv(BUFSIZE)
        if data == "" or data == "quit":
            # When the remote end is closed and all data is read, return the empty string.
            clientSock.close()
            break
        else:
            print 'recieve : ', data


def send_redisMsg():
    redis_client = redis.StrictRedis("127.0.0.1", 6379)
    download_msg = {
        "url": "https://shawblog.me",
        "path": "D:/",
        "filename": "index.html"
    }
    msg = {
        "topic": "socketTask",
        "content": {"appkey": "76d44f617b70c97e118c81dc579d9aa5", "contents": "quit"}
    }
    print (redis_client.publish("task_message", json.dumps(msg, sort_keys=True)))


if __name__ == '__main__':
    test_socket()
