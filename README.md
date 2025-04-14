# AIVK-QQ

基于 AIVK 框架的 QQ 机器人MCP 服务器实现
agent 前置项目

基于AIVK

## 快速开始

支持两种方式运行：
stdio / sse

uv tool install aivk_qq

设置aivk root 路径 aivk init --path /path/to/aivk/root/
AIVK_ROOT = /path/to/aivk/root/ OR 环境变量 AIVK_ROOT OR ~/.aivk （默认）

aivk-qq --path /path/to/aivk/root/

## bot_uid : 受控机器人的QQ号 root : 超级管理员QQ号
aivk-qq config --bot_uid xxx --root xxx (保存到AIVK_ROOT/etc/qq/config.toml)

## 配置mcp服务器

command:
    aivk-qq
args:
    "mcp"

这将以默认stdio方式启动

    
aivk-qq mcp --transport sse --port 10141 --host 127.0.0.1 
这将以sse方式启动
注意：你将启动在本地的10141端口上
localhost:10141
请访问：
loacalhost:10141/sse/


## 致谢

本项目基于以下开源项目：

- [ncatbot](https://github.com/liyihao1110/ncatbot) - 提供 QQ 机器人客户端实现
- [AIVK](https://github.com/LIghtJUNction/aivk) - AI虚拟内核框架
- [MCP](https://github.com/modelcontextprotocol/python-sdk) - Model Context Protocol

感谢所有这些项目的贡献者，使本项目成为可能。
