# Copyright (c) 2025 AIVK
# 
# 感谢 ncatbot (https://github.com/liyihao1110/ncatbot) 提供的机器人客户端支持
# 本项目使用了 ncatbot 作为 QQ 机器人客户端实现
#
# author: LIghtJUNction
# date: 2025-04-14

import logging

from pathlib import Path
import locale
from mcp.server.fastmcp import FastMCP
from aivk.api import AivkIO

try:
    from ..base.utils import setup_napcat
except ImportError:
    from aivk_qq.base.utils import setup_napcat

from mcp import types

# 配置日志格式，使用适当的编码设置避免中文乱码
# 获取当前系统编码
system_encoding = locale.getpreferredencoding()
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("aivk.qq.mcp")

aivk_qq_config = AivkIO.get_config("qq")
port = aivk_qq_config.get("port", 10141)
host = aivk_qq_config.get("host", "localhost")
transport = aivk_qq_config.get("transport", "stdio")

# 使用logger输出当前配置信息
logger.info(f"当前MCP服务器传输协议为: {transport}")
logger.info(f"当前配置: {aivk_qq_config}")
logger.info("服务已启动")

mcp = FastMCP(name="aivk_qq", instructions="AIVK QQ MCP Server" , port=port, host=host, debug=True)

aivk_qq_config["port"] = port
aivk_qq_config["host"] = host

AivkIO.add_module_id("qq")
AivkIO.add_module_id("qq_mcp")
AivkIO.save_config("qq", aivk_qq_config)

bot = setup_napcat()


bot.run_none_blocking()


@mcp.tool(name="ping", description="Ping the server")
def ping():
    """
    Ping the server
    """
    return "pong"


@mcp.tool(name="send_private_message", description="Send a private message")
def send_private_message(uid: int, message: str) -> str:
    """
    Send a private message to a user
    uid : User ID (QQ号)
    """
    logger.info(f"Send private message to {uid}: {message}")

    BotAPI.post_private_msg_sync(
        user_id=uid,
        message=message,
    )



if __name__ == "__main__":
    bot.run_none_blocking()
    mcp.run(transport=transport)
