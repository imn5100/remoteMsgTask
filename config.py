# -*- coding=utf-8 -*-
import os

WS_URL = 'ws://wst.shawblog.me/dolores/'
SUBSCRIBE_PREFIX = '/dolores/driver/'

TOKEN = 'b0510e1aa50921a127320c97b5279d17'
DEVICE_ID = '532e226fc744e6e2a99d1b851096d45a92abec36ad45473e'

# aria2配置 jsonrpc访问路径 和 aria2 路径,aria2 需要自己启动rpc服务

RPC_URL = "http://localhost:6800/jsonrpc?tm=%s"
# 是否必须开启aria2c
MUST_OPEN_ARIA2C = True

IS_WINDOWS = os.name == 'nt'
