# -*- coding=utf-8 -*-
# 登录验证
USER_AUTH = {"username": "*", "password": "*"}
# 消息topic
TOPIC = {
    "download": "download",
    "python": "python"
}
# 任务状态
STATUS_MAP = {
    "init": 1,
    "start": 2,
    "over": 3,
    "fail": 4,
}
# 脚本登录接口，ip必须为白名单ip
REMOTE_LOGIN_URL = "https://shawblog.me/blogger/script/login.do"
# 获取任务消息 200 成功有数据返回 201成功但无数据  1001 传参为空或格式错误 600因为异常操作失败
CONSUMER_URL = "https://shawblog.me/admin/remote/script/consumerMsg.do"
# id 操作的任务数据主键  type 1-4 重新启用任务 开启任务 完成任务 任务失败 默认为开启任务
CALLBACK_URL = "https://shawblog.me/admin/remote/script/callbackMsg.do"
# 检查是否登录成功
CHECK_URL = "https://shawblog.me/admin/main.jsp"
CHECK_STR = u"管理界面"
# aria2配置 jsonrpc访问路径 和 arai2 路径
RPC_URL = "http://localhost:6800/jsonrpc?tm=%s"
ARIA2_PATH = "aria2/"

# scoket 远程任务执行相关
APP_KEY = "*"
APP_SECRET = "*"
SERVER_ADDR = ('139.196.45.8', 8001)
