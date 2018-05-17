# -*- coding=utf-8 -*-
import os

WS_URL = 'ws://wst.shawblog.me/dolores/'
SUBSCRIBE_PREFIX = '/dolores/driver/'

TOKEN = '1401edeb55171b211916840bcc0eb7e7'
DEVICE_ID = 'fe73bd5d5e173c80e6ec7c23694a3af802a66c75008a2cb4'

# aria2配置 jsonrpc访问路径 和 aria2 路径,aria2 需要自己启动rpc服务

RPC_URL = "http://localhost:6800/jsonrpc?tm=%s"
# 是否必须开启aria2c
MUST_OPEN_ARIA2C = True

IS_WINDOWS = os.name == 'nt'
