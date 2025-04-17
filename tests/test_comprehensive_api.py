#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NapCat API 全面测试脚本
测试 NapCat API 的所有主要功能
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root (containing src) to sys.path
project_root = Path(__file__).resolve().parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple

# 为导入做准备
sys.path.insert(0, str(Path(__file__).parent.parent))

from aivk_qq.napcat.api import NapcatAPI, NapcatType
from aivk_qq.napcat.napcat import ApiResponseDict, NapcatClient
from aivk_qq.base.enums import ActionType, MessageSegmentType
from aivk_qq.base.message import Message

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("napcat_comprehensive_test")

# 测试配置
TEST_CONFIG = {
    "host": "127.0.0.1",
    "port": 10143,
    # 测试目标ID，可以根据需要修改
    "test_user_id": 2418701971,  # 测试用户QQ号
    "test_group_id": 12345678,   # 测试群号（如果要测试群功能）
    "test_message_id": "12345",  # 用于测试消息相关API的消息ID
    "test_file_path": "./test_file.txt",  # 测试文件路径
    "test_image_url": "https://example.com/image.jpg",  # 测试图片URL
    "test_timeout": 5,  # API请求超时时间（秒）
}

class ApiTestResult:
    """API测试结果类"""
    def __init__(self, name: str, success: bool, response: Dict[str, Any] = None, error: str = None):
        self.name = name
        self.success = success
        self.response = response
        self.error = error
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        if self.success:
            return f"✅ {self.name}: 成功 - {self.response}"
        else:
            return f"❌ {self.name}: 失败 - {self.error}"

class ComprehensiveApiTester:
    """全面的API测试类"""
    
    def __init__(self):
        """初始化测试类"""
        self.results = []
        # 修正：使用正确的方法创建HTTP客户端
        self.api = NapcatAPI.NapcatHttpClient(
            HOST=TEST_CONFIG["host"], 
            PORT=TEST_CONFIG["port"]
        )
        self.api.HTTP_CLIENT_CONNECT()  # 连接HTTP客户端
        # 修正：使用关键字参数初始化 NapcatClient
        self.client = NapcatClient(api=self.api)
        
        # 设置默认的机器人QQ号，用于测试环境
        self.client.set_default_self_id(user_id=3481455217)  # 假设机器人QQ号为10000
        
        # 记录API端点名称及其测试状态
        self.api_endpoints = {}
        for action in ActionType:
            self.api_endpoints[action.value] = {"tested": False, "result": None}
    
    async def run_test(self, test_func, *args, **kwargs) -> ApiTestResult:
        """运行单个测试并记录结果"""
        test_name: Any = test_func.__name__
        try:
            response: Any = await test_func(*args, **kwargs)
            result: ApiTestResult = ApiTestResult(test_name, True, response)
            
            # 标记相关的API端点为已测试
            endpoint_name = test_name.replace("test_", "")
            if endpoint_name in self.api_endpoints:
                self.api_endpoints[endpoint_name]["tested"] = True
                self.api_endpoints[endpoint_name]["result"] = result
                
            logger.info(msg=f"测试 {test_name} 成功: {response}")
        except Exception as e:
            result: ApiTestResult = ApiTestResult(test_name, False, error=str(e))
            logger.error(f"测试 {test_name} 失败: {e}")
        
        self.results.append(result)
        return result
    
    def print_summary(self) -> None:
        """打印测试结果摘要"""
        total: int = len(self.results)
        success: int = sum(1 for r in self.results if r.success)
        logger.info(msg=f"测试摘要: 总共 {total} 项测试, 成功 {success} 项, 失败 {total - success} 项")
        
        # 打印未测试的API端点
        untested = [name for name, info in self.api_endpoints.items() if not info["tested"]]
        if untested:
            logger.warning(f"未测试的API端点 ({len(untested)}): {', '.join(untested)}")
        
        # 打印失败的测试
        failures: list[Any] = [r for r in self.results if not r.success]
        if failures:
            logger.error(msg="失败的测试:")
            for f in failures:
                logger.error(msg=f"  {f}")
    
    # ========================== API 测试方法 ==========================
    # 每个方法对应一个API端点，方法名与端点名一致以便记忆
    
    # ========== 消息发送相关 ==========
    
    async def test_send_private_msg(self) -> Dict[str, Any]:
        """测试发送私聊消息"""
        user_id = TEST_CONFIG["test_user_id"]
        result = await self.client.send_private_msg(
            user_id=user_id, 
            message=f"这是一条测试私聊消息 - {datetime.now()}"
        )
        return result
    
    async def test_send_group_msg(self) -> Dict[str, Any]:
        """测试发送群消息"""
        if not TEST_CONFIG.get("test_group_id"):
            return {"status": "skipped", "message": "未配置测试群号"}
        
        group_id: str | int = TEST_CONFIG["test_group_id"]
        result: ApiResponseDict = await self.client.send_group_msg(
            group_id=group_id, 
            message=f"这是一条测试群消息 - {datetime.now()}"
        )
        return result
    
    async def test_send_msg(self) -> Dict[str, Any]:
        """测试发送消息(通用)"""
        user_id: str | int = TEST_CONFIG["test_user_id"]
        result: ApiResponseDict = await self.client.send_msg(
            message_type="private",
            id=user_id,
            message=f"这是一条通用API测试消息 - {datetime.now()}"
        )
        return result
    
    async def test_send_text(self) -> Dict[str, Any]:
        """测试发送纯文本消息"""
        user_id = TEST_CONFIG["test_user_id"]
        result = await self.client.send_text(
            target_type="private",
            target_id=user_id,
            text=f"这是一条纯文本测试消息 - {datetime.now()}"
        )
        return result
    
    async def test_send_image(self) -> Dict[str, Any]:
        """测试发送图片消息"""
        user_id = TEST_CONFIG["test_user_id"]
        result = await self.client.send_image(
            target_type="private",
            target_id=user_id,
            file=TEST_CONFIG["test_image_url"]
        )
        return result
    
    async def test_send_forward_msg(self) -> Dict[str, Any]:
        """测试发送合并转发消息"""
        user_id = TEST_CONFIG["test_user_id"]
        
        # 创建转发消息节点
        nodes = self.client.create_forward_nodes([
            (10001, "转发消息测试1", "这是第一条转发消息"),
            (10002, "转发消息测试2", "这是第二条转发消息"),
            (10003, "转发消息测试3", "这是第三条转发消息"),
        ])
        
        result = await self.client.send_forward_msg(
            target_type="private",
            target_id=user_id,
            messages=nodes
        )
        return result
    
    # ========== 消息操作相关 ==========
    
    async def test_delete_msg(self) -> Dict[str, Any]:
        """测试撤回消息"""
        # 首先发送一条消息，然后撤回它
        user_id = TEST_CONFIG["test_user_id"]
        send_result = await self.client.send_private_msg(
            user_id=user_id, 
            message=f"这条消息将被撤回 - {datetime.now()}"
        )
        
        # 提取消息ID (实际中应从send_result中获取，但模拟环境可能没有返回)
        message_id = send_result.get("data", {}).get("message_id") or TEST_CONFIG["test_message_id"]
        
        # 撤回消息
        result = await self.client.recall_message(message_id)
        return result
    
    async def test_get_msg(self) -> Dict[str, Any]:
        """测试获取消息"""
        message_id = TEST_CONFIG["test_message_id"]
        result = await self.client.get_message(message_id)
        return result
    
    # ========== 用户信息相关 ==========
    
    async def test_get_login_info(self) -> Dict[str, Any]:
        """测试获取登录信息"""
        result = await self.client.get_login_info()
        return result
    
    async def test_get_stranger_info(self) -> Dict[str, Any]:
        """测试获取陌生人信息"""
        user_id = TEST_CONFIG["test_user_id"]
        result = await self.client._call_action(ActionType.GET_STRANGER_INFO, {
            "user_id": user_id,
            "no_cache": True
        })
        return result
    
    async def test_get_friend_list(self) -> Dict[str, Any]:
        """测试获取好友列表"""
        result = await self.client._call_action(ActionType.GET_FRIEND_LIST)
        return result
    
    # ========== 群组相关 ==========
    
    async def test_get_group_list(self) -> Dict[str, Any]:
        """测试获取群列表"""
        result = await self.client._call_action(ActionType.GET_GROUP_LIST)
        return result
    
    async def test_get_group_info(self) -> Dict[str, Any]:
        """测试获取群信息"""
        if not TEST_CONFIG.get("test_group_id"):
            return {"status": "skipped", "message": "未配置测试群号"}
        
        group_id = TEST_CONFIG["test_group_id"]
        result = await self.client._call_action(ActionType.GET_GROUP_INFO, {
            "group_id": group_id,
            "no_cache": True
        })
        return result
    
    async def test_get_group_member_list(self) -> Dict[str, Any]:
        """测试获取群成员列表"""
        if not TEST_CONFIG.get("test_group_id"):
            return {"status": "skipped", "message": "未配置测试群号"}
        
        group_id = TEST_CONFIG["test_group_id"]
        result = await self.client._call_action(ActionType.GET_GROUP_MEMBER_LIST, {
            "group_id": group_id
        })
        return result
    
    # ========== 扩展功能测试 ==========
    
    async def test_special_message_types(self) -> Dict[str, Any]:
        """测试特殊消息类型"""
        user_id = TEST_CONFIG["test_user_id"]
        results = {}
        
        # 测试链接分享
        try:
            share_result = await self.client.send_share(
                target_type="private",
                target_id=user_id,
                url="https://example.com",
                title="测试链接分享",
                content="这是分享的内容描述"
            )
            results["share"] = share_result
        except Exception as e:
            results["share"] = {"error": str(e)}
        
        # 测试位置分享
        try:
            location_result = await self.client.send_location(
                target_type="private",
                target_id=user_id,
                lat=39.9,
                lon=116.3,
                title="测试位置",
                content="北京市"
            )
            results["location"] = location_result
        except Exception as e:
            results["location"] = {"error": str(e)}
        
        # 测试音乐分享
        try:
            music_result = await self.client.send_music(
                target_type="private",
                target_id=user_id,
                music_type="163",
                music_id="28949129"
            )
            results["music"] = music_result
        except Exception as e:
            results["music"] = {"error": str(e)}
        
        # 测试自定义音乐分享
        try:
            custom_music_result = await self.client.send_custom_music(
                target_type="private",
                target_id=user_id,
                url="https://example.com/music",
                audio="https://example.com/music.mp3",
                title="测试自定义音乐",
                content="这是一首自定义音乐"
            )
            results["custom_music"] = custom_music_result
        except Exception as e:
            results["custom_music"] = {"error": str(e)}
        
        return results
    
    async def test_at_message(self) -> Dict[str, Any]:
        """测试@消息功能"""
        if not TEST_CONFIG.get("test_group_id"):
            return {"status": "skipped", "message": "未配置测试群号"}
        
        group_id = TEST_CONFIG["test_group_id"]
        result = await self.client.send_at_message(
            group_id=group_id,
            user_id="all",  # @全体成员
            text="这是一条@全体成员的测试消息"
        )
        return result
    
    async def test_message_parsing(self) -> Dict[str, Any]:
        """测试消息解析功能"""
        # 创建复杂消息
        message = self.client.create_message()
        message.text("这是测试文本").face(1).image(TEST_CONFIG["test_image_url"]).at(10001)
        
        # 测试解析
        results = {}
        msg_segments = message.get_segments()
        
        # 解析为Message对象
        parsed_message = self.client.parse_message(msg_segments)
        
        # 测试提取纯文本
        results["plain_text"] = self.client.get_message_text(parsed_message)
        
        # 测试提取图片URL
        results["image_urls"] = self.client.get_message_images(parsed_message)
        
        # 测试提取@目标
        results["at_targets"] = self.client.get_at_targets(parsed_message)
        
        # 测试检查是否@全体成员
        results["has_at_all"] = self.client.has_at_all(parsed_message)
        
        return results
    
    # ========== 文件操作测试 ==========
    
    async def test_upload_group_file(self):
        """测试上传群文件"""
        if not TEST_CONFIG.get("test_group_id"):
            return {"status": "skipped", "message": "未配置测试群号"}
        
        # 创建测试文件
        with open(TEST_CONFIG["test_file_path"], 'w') as f:
            f.write("test content")
        
        group_id = TEST_CONFIG["test_group_id"]
        result = await self.client._call_action(
            ActionType.UPLOAD_GROUP_FILE,
            {
                "group_id": group_id,
                "file": TEST_CONFIG["test_file_path"],
                "name": "test_upload.txt"
            }
        )
        return result

    async def test_get_group_file_list(self):
        """测试获取群文件列表"""
        if not TEST_CONFIG.get("test_group_id"):
            return {"status": "skipped", "message": "未配置测试群号"}
        
        group_id = TEST_CONFIG["test_group_id"]
        result = await self.client._call_action(
            ActionType.GET_GROUP_ROOT_FILES,
            {"group_id": group_id}
        )
        return result

    # ========== 工具方法 ==========
    
    async def test_all_apis(self):
        """测试所有API端点"""
        # 基本消息发送测试
        await self.run_test(self.test_send_private_msg)
        await self.run_test(self.test_send_msg)
        await self.run_test(self.test_send_text)
        await self.run_test(self.test_send_image)
        
        # 如果配置了测试群号，测试群相关功能
        if TEST_CONFIG.get("test_group_id"):
            await self.run_test(self.test_send_group_msg)
            await self.run_test(self.test_at_message)
            await self.run_test(self.test_get_group_info)
            await self.run_test(self.test_get_group_member_list)
        
        # 测试消息操作
        await self.run_test(self.test_delete_msg)
        await self.run_test(self.test_get_msg)
        
        # 测试用户信息
        await self.run_test(self.test_get_login_info)
        await self.run_test(self.test_get_stranger_info)
        await self.run_test(self.test_get_friend_list)
        
        # 测试群组信息
        await self.run_test(self.test_get_group_list)
        
        # 测试转发消息
        await self.run_test(self.test_send_forward_msg)
        
        # 测试特殊消息类型
        await self.run_test(self.test_special_message_types)
        
        # 测试文件操作
        await self.run_test(self.test_upload_group_file)
        await self.run_test(self.test_get_group_file_list)
        
        # 测试消息解析功能
        await self.run_test(self.test_message_parsing)
        
        # 打印测试摘要
        self.print_summary()

async def main():
    """主函数"""
    logger.info("=== 全面 API 测试开始 ===")
    
    tester = ComprehensiveApiTester()
    await tester.test_all_apis()
    
    logger.info("=== 全面 API 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(main())