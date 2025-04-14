# Copyright (c) 2025 AIVK
# 
# 感谢 ncatbot (https://github.com/liyihao1110/ncatbot) 提供的机器人客户端支持
# 本项目使用了 ncatbot 作为 QQ 机器人客户端实现
#
# author: LIghtJUNction
# date: 2025-04-14

import logging
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from aivk.api import AivkIO
from typing import Dict, Any, List, Optional
try:
    from ..base.utils import setup_napcat
except ImportError:
    from aivk_qq.base.utils import setup_napcat

from ncatbot.core import GroupMessage, PrivateMessage

from mcp import types

logger = logging.getLogger("aivk.qq.mcp")

aivk_qq_config = AivkIO.get_config("qq")
port = aivk_qq_config.get("port", 10141)
host = aivk_qq_config.get("host", "localhost")
transport = aivk_qq_config.get("transport", "stdio")

mcp = FastMCP(name="aivk_qq", instructions="AIVK QQ MCP Server" , port=port, host=host, debug=True)

aivk_qq_config["port"] = port
aivk_qq_config["host"] = host

AivkIO.add_module_id("qq")
AivkIO.add_module_id("qq_mcp")
AivkIO.save_config("qq", aivk_qq_config)

bot = setup_napcat()

@mcp.tool(name="ping", description="Ping the server")
def ping():
    """
    Ping the server
    """
    return "pong"

async def on_group_message(msg: GroupMessage):
    """
    Group message handler
    """

    logger.info(f"Group message: {msg}")
    if msg.raw_message == "测试":
        await msg.reply(text="NcatBot 测试成功喵~")
    # 处理群消息
    return msg


async def on_private_message(msg: PrivateMessage):
    """
    Private message handler
    """

    logger.info(f"Private message: {msg}")

    @mcp.resource("qq://test")
    def test():
        return "This is a test response."

    if msg.raw_message == "测试":
        await msg.reply(text="NcatBot 测试成功喵~")
    # 处理私聊消息
    return msg

bot.run()
if __name__ == "__main__":
    
    mcp.run(transport=transport)
    