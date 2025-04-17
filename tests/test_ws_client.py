#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NapCat WebSocket 客户端测试脚本
测试 NapCat API 的 WebSocket 客户端功能和高级封装
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Any

# Add project root (containing src) to sys.path
project_root = Path(__file__).resolve().parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from aivk_qq.napcat.api import NapcatAPI, NapcatPort
from aivk_qq.napcat.napcat import NapcatClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("napcat_ws_test")

# 测试配置
TARGET_QQ = 2418701971  # 测试用户QQ
HOST = "127.0.0.1"
PORT = NapcatPort.WS_CLIENT.value
TOKEN = str(PORT)  # 使用端口号作为token
TEST_GROUP = None  # 如果需要测试群功能，这里填写群号
TEST_DURATION = 30  # 测试运行时间（秒）

# 用于保存测试状态和结果
test_results: dict[str, Any] = {
    "connected": False,
    "message_received": False,
    "self_id": None,
    "received_messages": []
}

# 标记是否要关闭连接
should_exit: bool = False

async def send_test_messages(client):
    """发送测试消息"""
    try:
        # 等待连接完全建立
        await asyncio.sleep(2)
        
        logger.info(f"发送测试消息到 {TARGET_QQ}...")
        
        # 发送简单文本消息
        await client.send_text("private", TARGET_QQ, "这是一条WebSocket客户端测试消息")
        
        # 发送复杂消息
        message = client.create_message()
        message.text("这是一条复杂消息，包含：").face(1).text("\n- 表情").image(
            "https://i0.hdslb.com/bfs/archive/c89cb719ad565587ff34e5ef9acf4bb703a0f6a1.jpg@672w_378h_1c_!web-search-common-cover.avif"
        )
        await client.send_private_msg(TARGET_QQ, message)
        
        # 如果设置了测试群，发送群消息
        if TEST_GROUP:
            await client.send_text("group", TEST_GROUP, "WebSocket客户端群消息测试")
            await client.send_at_message(TEST_GROUP, TARGET_QQ, "这是一条@消息测试")
        
        logger.info("测试消息发送完成")
        
    except Exception as e:
        logger.error(f"发送测试消息失败: {e}")

async def handle_exit(client):
    """处理退出信号"""
    global should_exit
    should_exit = True
    logger.info("准备关闭连接...")
    await client.stop()
    logger.info("连接已关闭，测试结束")

async def main():
    """主测试函数"""
    global should_exit
    
    # 创建API实例
    api = NapcatAPI.NapcatWebSocketClient(
        HOST=HOST,
        PORT=PORT,
        TOKEN=TOKEN,
        NAME="测试WS客户端"
    )
    
    # 创建高级封装客户端
    client = NapcatClient.WS_CLIENT(api)
    
    # 注册事件处理函数
    @client.on("meta_event.lifecycle.connect")
    async def handle_connect(event):
        """处理连接成功事件"""
        logger.info("WebSocket连接已建立！")
        test_results["connected"] = True
        
        # 连接成功后发送测试消息
        await send_test_messages(client)
    
    @client.on_message()
    async def handle_message(event):
        """处理所有消息事件"""
        logger.info(f"收到消息事件: {event}")
        test_results["message_received"] = True
        test_results["received_messages"].append(event)
        
        # 解析消息内容
        message = event.get("message", [])
        message_text = client.get_message_text(message)
        logger.info(f"消息文本: {message_text}")
        
        # 如果是目标用户的消息，进行回复
        if event.get("user_id") == TARGET_QQ:
            # 如果是私聊消息
            if event.get("message_type") == "private":
                await client.send_reply("private", TARGET_QQ, event.get("message_id"), 
                                       f"已收到你的消息: {message_text}")
            # 如果是群聊消息
            elif event.get("message_type") == "group" and TEST_GROUP:
                if client.is_at_me(event, test_results["self_id"]):
                    await client.send_reply("group", event.get("group_id"), event.get("message_id"),
                                           f"已收到你的@消息: {message_text}")
    
    @client.on_meta_event("heartbeat")
    async def handle_heartbeat(event):
        """处理心跳事件"""
        # 记录机器人QQ号
        if not test_results["self_id"] and "self_id" in event:
            test_results["self_id"] = event.get("self_id")
            logger.info(f"已获取机器人QQ号: {test_results['self_id']}")
    
    try:
        # 启动客户端
        logger.info("启动WebSocket客户端...")
        await client.start()
        
        # 等待连接建立
        try:
            await client.wait_for_connected(timeout=10)
            logger.info("WebSocket连接已建立")
        except asyncio.TimeoutError:
            logger.error("等待WebSocket连接超时")
            return
        
        # 设置测试运行时间限制
        logger.info(f"测试将运行 {TEST_DURATION} 秒...")
        end_time = time.time() + TEST_DURATION
        
        # 运行测试
        while not should_exit and time.time() < end_time:
            await asyncio.sleep(1)
        
        if not should_exit:
            logger.info("测试时间到，准备退出")
            should_exit = True
            
    except KeyboardInterrupt:
        logger.info("接收到键盘中断信号")
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        # 打印详细堆栈信息
        import traceback
        traceback.print_exc()
    finally:
        # 确保客户端正确关闭
        await client.stop()
        logger.info("测试完成，结果汇总：")
        logger.info(f"连接成功: {test_results['connected']}")
        logger.info(f"收到消息: {test_results['message_received']}")
        logger.info(f"机器人QQ: {test_results['self_id']}")
        logger.info(f"收到消息数量: {len(test_results['received_messages'])}")

if __name__ == "__main__":
    # 直接运行主测试函数，避免使用不支持的信号处理
    asyncio.run(main())