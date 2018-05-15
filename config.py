# -*- coding=utf-8 -*-
import os

TOKEN = 'bf3948826a9eab85969ba73748a5c45a'
DEVICE_ID = 'fe73bd5d5e173c80e6ec7c23694a3af802a66c75008a2cb4'

# aria2配置 jsonrpc访问路径 和 aria2 路径,aria2 需要自己启动rpc服务

RPC_URL = "http://localhost:6800/jsonrpc?tm=%s"

IS_WINDOWS = os.name == 'nt'
