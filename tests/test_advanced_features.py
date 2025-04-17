#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NapCat 高级功能测试脚本
测试 NapCat API 的高级封装和实用工具
"""

import json
from typing import Any, Literal


from logging import Logger


import asyncio
import logging
import sys
from pathlib import Path

# Add project root (parent of tests and src) to sys.path
project_root: Path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from aivk_qq.napcat.api import NapcatAPI, NapcatPort
from aivk_qq.napcat.napcat import NapcatClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger: Logger = logging.getLogger(name="napcat_advanced_test")

# 测试配置
TARGET_QQ = 2418701971  # 测试用户QQ
HOST = "127.0.0.1"
PORT = NapcatPort.HTTP_CLIENT.value  # 使用HTTP客户端进行测试
TOKEN = str(PORT)  # 使用端口号作为token
TEST_GROUP = None  # 如果需要测试群功能，这里填写群号

async def test_message_building() -> Literal['消息构建测试完成']:
    """测试消息构建功能"""
    logger.info(msg="=== 测试消息构建功能 ===")
    
    # 创建API实例
    api: NapcatAPI = NapcatAPI.NapcatHttpClient(
        HOST=HOST,
        PORT=PORT,
        TOKEN=TOKEN,
        NAME="高级功能测试客户端"
    )
    
    # 创建高级封装客户端
    client: NapcatClient = NapcatClient.HTTP_CLIENT(api)
    
    # 1. 测试基本消息构建
    logger.info(msg="测试基本消息构建...")
    message: Any = client.create_message()
    message.text("这是基本消息构建测试").face(1).text("\n添加了表情和文本")
    
    # 将消息段转换为列表并打印
    segments: Any = message.get_segments()
    logger.info(msg=f"消息段列表: {json.dumps(obj=segments, ensure_ascii=False)}")
    
    # 发送构建的消息
    result: Any = await client.send_private_msg(user_id=TARGET_QQ, message)
    logger.info(msg=f"发送结果: {result}")
    
    # 2. 测试复杂消息构建 - 包含多种消息类型
    logger.info(msg="测试复杂消息构建...")
    complex_message: Any = client.create_message()
    complex_message.text("这是一条复杂消息，包含多种元素：\n")
    complex_message.face(0)  # 添加表情
    complex_message.text("\n1. 文本与表情\n")
    complex_message.image("https://i1.hdslb.com/bfs/archive/efe004357ffa13f6730d6cfd85f8a0346cd9ba90.jpg@672w_378h_1c_!web-home-common-cover.avif")  # 添加图片
    complex_message.text("\n2. 网络图片\n")
    
    # 发送复杂消息
    result = await client.send_private_msg(TARGET_QQ, complex_message)
    logger.info(f"复杂消息发送结果: {result}")
    
    # 3. 测试消息解析功能
    test_message: list[dict[str, str | dict[str, str]]] = [
        {"type": "text", "data": {"text": "这是测试文本"}},
        {"type": "face", "data": {"id": "1"}},
        {"type": "at", "data": {"qq": "10001"}},
        {"type": "image", "data": {"url": "https://example.com/image.jpg"}}
    ]
    
    # 从消息段解析
    parsed_message: Any = client.parse_message(message=test_message)
    plain_text: str = client.get_message_text(message=parsed_message)
    logger.info(msg=f"解析得到的纯文本: {plain_text}")
    
    # 提取图片URL
    image_urls: list[str] = client.get_message_images(message=parsed_message)
    logger.info(msg=f"提取的图片URLs: {image_urls}")
    
    # 提取@目标
    at_targets: list[str] = client.get_at_targets(message=parsed_message)
    logger.info(msg=f"提取的@目标: {at_targets}")
    
    return "消息构建测试完成"

async def test_special_messages():
    """测试特殊消息类型"""
    logger.info("=== 测试特殊消息类型 ===")
    
    # 创建API实例
    api = NapcatAPI.NapcatHttpClient(
        HOST=HOST,
        PORT=PORT,
        TOKEN=TOKEN,
        NAME="特殊消息测试客户端"
    )
    
    # 创建高级封装客户端
    client = NapcatClient.HTTP_CLIENT(api)
    
    # 1. 测试分享链接
    logger.info("测试分享链接...")
    try:
        share_result = await client.send_share(
            "private", 
            TARGET_QQ, 
            url="https://github.com/lightpursuer/aivk-qq",
            title="AIVK-QQ项目",
            content="一个优秀的QQ机器人框架",
            image="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        )
        logger.info(f"分享链接结果: {share_result}")
    except Exception as e:
        logger.error(f"分享链接失败: {e}")
    
    # 2. 测试音乐分享
    logger.info("测试音乐分享...")
    try:
        music_result = await client.send_music(
            "private",
            TARGET_QQ,
            music_type="163",  # 网易云音乐
            music_id="1967525806"  # 音乐ID
        )
        logger.info(f"音乐分享结果: {music_result}")
    except Exception as e:
        logger.error(f"音乐分享失败: {e}")
    
    # 3. 测试自定义音乐分享
    logger.info("测试自定义音乐分享...")
    try:
        custom_music_result = await client.send_custom_music(
            "private",
            TARGET_QQ,
            url="https://y.music.163.com/m/song?id=1967525806",
            audio="http://music.163.com/song/media/outer/url?id=1967525806.mp3",
            title="自定义音乐测试",
            content="这是一个自定义音乐分享测试",
            image="https://p2.music.126.net/AtMEADx0M0z9-DG1ZGqYSA==/109951167826256354.jpg"
        )
        logger.info(f"自定义音乐分享结果: {custom_music_result}")
    except Exception as e:
        logger.error(f"自定义音乐分享失败: {e}")
    
    # 4. 测试合并转发消息
    logger.info("测试合并转发消息...")
    try:
        # 创建几个消息节点
        nodes = client.create_forward_nodes([
            (10001, "用户1", "这是第一条消息"),
            (10002, "用户2", "这是第二条消息，带表情[CQ:face,id=1]"),
            (10003, "用户3", [{"type": "text", "data": {"text": "这是第三条消息，使用消息段列表"}}])
        ])
        
        # 发送合并转发消息
        forward_result = await client.send_forward_msg("private", TARGET_QQ, nodes)
        logger.info(f"合并转发结果: {forward_result}")
    except Exception as e:
        logger.error(f"合并转发消息失败: {e}")
    
    # 5. 测试位置分享
    logger.info("测试位置分享...")
    try:
        location_result = await client.send_location(
            "private",
            TARGET_QQ,
            lat=39.9087243069,
            lon=116.3974797568,
            title="天安门广场",
            content="北京市东城区东长安街"
        )
        logger.info(f"位置分享结果: {location_result}")
    except Exception as e:
        logger.error(f"位置分享失败: {e}")
    
    return "特殊消息类型测试完成"

async def test_group_operations():
    """测试群操作功能（仅当配置了测试群时执行）"""
    if not TEST_GROUP:
        logger.warning("未配置测试群，跳过群操作测试")
        return "未执行群操作测试"
    
    logger.info("=== 测试群操作功能 ===")
    
    # 创建API实例
    api = NapcatAPI.NapcatHttpClient(
        HOST=HOST,
        PORT=PORT,
        TOKEN=TOKEN,
        NAME="群操作测试客户端"
    )
    
    # 创建高级封装客户端
    client = NapcatClient.HTTP_CLIENT(api)
    
    # 1. 获取群信息
    logger.info(f"获取群 {TEST_GROUP} 信息...")
    try:
        group_info = await client._call_action("get_group_info", {
            "group_id": TEST_GROUP
        })
        logger.info(f"群信息: {group_info}")
    except Exception as e:
        logger.error(f"获取群信息失败: {e}")
    
    # 2. 获取群成员列表
    logger.info(f"获取群 {TEST_GROUP} 成员列表...")
    try:
        member_list = await client._call_action("get_group_member_list", {
            "group_id": TEST_GROUP
        })
        logger.info(f"成员数量: {len(member_list.get('data', []))}")
    except Exception as e:
        logger.error(f"获取群成员列表失败: {e}")
    
    # 3. 测试@全体成员(可能会受限制)
    logger.info("测试@全体成员...")
    try:
        at_all_message = client.create_message().at_all().text(" 这是一条@全体成员的测试消息")
        at_all_result = await client.send_group_msg(TEST_GROUP, at_all_message)
        logger.info(f"@全体成员结果: {at_all_result}")
    except Exception as e:
        logger.error(f"@全体成员失败: {e}")
    
    # 4. 测试群公告发送
    logger.info("测试发送群公告...")
    try:
        notice_result = await client._call_action("_send_group_notice", {
            "group_id": TEST_GROUP,
            "content": "这是一条测试公告，由API测试程序发送"
        })
        logger.info(f"发送群公告结果: {notice_result}")
    except Exception as e:
        logger.error(f"发送群公告失败: {e}")
    
    return "群操作测试完成"

async def main():
    """主测试函数"""
    try:
        # 测试消息构建
        result1 = await test_message_building()
        logger.info(result1)
        
        # 等待一段时间避免消息发送过快
        await asyncio.sleep(2)
        
        # 测试特殊消息类型
        result2 = await test_special_messages()
        logger.info(result2)
        
        # 等待一段时间避免消息发送过快
        await asyncio.sleep(2)
        
        # 测试群操作功能
        result3 = await test_group_operations()
        logger.info(result3)
        
        logger.info("所有测试完成！")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())