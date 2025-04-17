#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NapCat HTTP 客户端测试脚本
测试 NapCat API 的 HTTP 客户端功能和高级封装
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root (containing src) to sys.path
project_root = Path(__file__).resolve().parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from aivk_qq.napcat.api import NapcatAPI, NapcatPort
from aivk_qq.napcat.napcat import ApiResponseDict, NapcatClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("napcat_http_test")

# 测试配置
TARGET_QQ = 2418701971  # 测试用户QQ
HOST = "127.0.0.1"
PORT = NapcatPort.HTTP_CLIENT.value
TOKEN = str(PORT)  # 使用端口号作为token
TEST_GROUP = None  # 如果需要测试群功能，这里填写群号

async def test_http_client():
    """测试 HTTP 客户端基本功能"""
    logger.info("开始 HTTP 客户端测试")
    
    # 创建API实例
    api = NapcatAPI.NapcatHttpClient(
        HOST=HOST,
        PORT=PORT,
        TOKEN=TOKEN,
        NAME="测试客户端"
    )
    
    # 创建高级封装客户端
    client: NapcatClient = NapcatClient.HTTP_CLIENT(api)
    
    # 测试获取登录信息
    try:
        logger.info(msg="测试获取登录信息...")
        login_info: ApiResponseDict = await client._call_action(action="get_login_info")
        logger.info(msg=f"登录信息: {login_info}")
        
        # 提取机器人自己的QQ号
        self_id = login_info.get("data", {}).get("user_id")
        if self_id:
            logger.info(f"机器人QQ: {self_id}")
        else:
            logger.warning("未能获取机器人QQ号")
    except Exception as e:
        logger.error(f"获取登录信息失败: {e}")
    
    # 测试发送私聊消息
    try:
        logger.info(f"测试发送私聊消息到 {TARGET_QQ}...")
        
        # 测试纯文本消息
        text_result = await client.send_text("private", TARGET_QQ, "这是一条测试消息，通过HTTP客户端发送")
        logger.info(f"文本消息发送结果: {text_result}")
        
        # 测试消息构建器
        message = client.create_message().text("这是通过构建器创建的消息").face(0).text("\n包含表情和文本")
        build_result = await client.send_private_msg(TARGET_QQ, message)
        logger.info(f"构建消息发送结果: {build_result}")
        
        # 测试图片消息（使用网络图片）
        img_url = "https://i0.hdslb.com/bfs/archive/c89cb719ad565587ff34e5ef9acf4bb703a0f6a1.jpg@672w_378h_1c_!web-search-common-cover.avif"
        img_result = await client.send_image("private", TARGET_QQ, img_url)
        logger.info(f"图片消息发送结果: {img_result}")
        
    except Exception as e:
        logger.error(f"发送私聊消息失败: {e}")
    
    # 如果配置了群号，测试群消息功能
    if TEST_GROUP:
        try:
            logger.info(f"测试发送群消息到群 {TEST_GROUP}...")
            
            # 测试群消息
            group_result = await client.send_text("group", TEST_GROUP, "这是一条测试群消息")
            logger.info(f"群消息发送结果: {group_result}")
            
            # 测试@功能
            at_result = await client.send_at_message(TEST_GROUP, TARGET_QQ, "你好，这是一条@消息测试")
            logger.info(f"@消息发送结果: {at_result}")
            
        except Exception as e:
            logger.error(f"发送群消息失败: {e}")
    
    # 测试获取好友列表
    try:
        logger.info("测试获取好友列表...")
        friend_list = await client._call_action("get_friend_list")
        logger.info(f"好友数量: {len(friend_list.get('data', []))}")
    except Exception as e:
        logger.error(f"获取好友列表失败: {e}")
    
    logger.info("HTTP 客户端测试完成")

if __name__ == "__main__":
    asyncio.run(test_http_client())