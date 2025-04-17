#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIVK-QQ API 低级接口示例

这个示例展示了AIVK-QQ中NapcatAPI的基本用法，包括:
1. HTTP客户端
2. HTTP SSE客户端
3. WebSocket客户端
4. HTTP服务器
5. WebSocket服务器

作者: light
日期: 2025-04-17
"""

import asyncio
import json
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("aivk.qq.example")

# 导入AIVK-QQ相关模块
from aivk.api import AivkIO
from aivk_qq.napcat.api import NapcatAPI

# ======== 工具函数 ========

async def send_and_receive(api_client, message):
    """发送消息并接收响应的通用方法"""
    logger.info(f"发送消息: {message}")
    response = await api_client.send_message(message)
    logger.info(f"接收响应: {response}")
    return response

def print_section(title):
    """打印带有分隔线的节标题"""
    print("\n" + "="*50)
    print(f" {title} ".center(50, "="))
    print("="*50)
    
# ======== 示例函数 ========

async def http_client_example():
    """HTTP客户端示例"""
    print_section("HTTP客户端示例")
    
    # 创建HTTP客户端
    http_client = NapcatAPI.NapcatHttpClient(
        HOST="127.0.0.1",
        PORT=10146,  # HTTP服务器端口
        TOKEN="your_token_here",  # 可选的认证令牌
        NAME="example_http_client", 
        MSGTYPE="Array"  # 或 "String"
    )
    
    # 连接到服务器
    http_client.HTTP_CLIENT_CONNECT()
    logger.info(f"HTTP客户端已连接到 {http_client.host}:{http_client.port}")
    
    try:
        # 发送消息示例
        # 1. 发送私聊消息
        private_msg = {
            "action": "send_private_msg",
            "params": {
                "user_id": 123456789,
                "message": "你好，这是AIVK-QQ HTTP客户端发送的消息"
            }
        }
        
        # 使用HTTP POST请求发送消息
        url = "/send_private_msg"  # 相对路径，基于base_url
        async with http_client.HTTP_CLIENT.post(
            url, 
            json=private_msg
        ) as response:
            result = await response.json()
            logger.info(f"发送私聊消息响应: {result}")
            
        # 2. 获取机器人信息
        url = "/get_login_info"
        async with http_client.HTTP_CLIENT.get(url) as response:
            result = await response.json()
            logger.info(f"机器人信息: {result}")
            
        # 如果启用了WebSocket，也可以通过WebSocket发送消息
        if http_client.WS_CLIENT:
            logger.info("通过WebSocket发送消息...")
            # 连接WebSocket
            websocket = await http_client.WS_CLIENT
            # 发送消息
            await websocket.send(json.dumps(private_msg))
            # 接收响应
            response = await websocket.recv()
            logger.info(f"WebSocket响应: {response}")
            # 关闭WebSocket连接
            await websocket.close()
            
    finally:
        # 关闭HTTP客户端会话
        await http_client.HTTP_CLIENT.close()
        logger.info("HTTP客户端已关闭")
    
    return "HTTP客户端示例完成"

async def sse_client_example():
    """HTTP SSE客户端示例 - 用于接收事件流"""
    print_section("HTTP SSE客户端示例")
    
    # 创建SSE客户端
    sse_client = NapcatAPI.NapcatHttpSSEClient(
        HOST="127.0.0.1",
        PORT=10144,  # SSE服务器端口
        TOKEN="your_token_here",  # 可选的认证令牌
        NAME="example_sse_client",
        WS=True  # 同时启用WebSocket
    )
    
    # 异步连接到SSE服务器
    await sse_client.HTTP_CLIENT_CONNECT_SSE()
    logger.info(f"SSE客户端已连接到 {sse_client.host}:{sse_client.port}")
    
    try:
        # 设置事件监听的超时时间
        timeout = 30  # 30秒
        start_time = asyncio.get_event_loop().time()
        
        # 开始监听事件流
        logger.info("开始监听SSE事件流...")
        async for event in sse_client.sse_events():
            event_type = event.get('event', 'unknown')
            event_data = event.get('data', '{}')
            
            logger.info(f"收到事件类型: {event_type}")
            logger.info(f"事件数据: {event_data}")
            
            # 处理不同类型的事件
            if event_type == "message":
                # 处理普通消息事件
                try:
                    data = json.loads(event_data)
                    if data.get("post_type") == "message":
                        logger.info("收到新消息!")
                        # 这里可以添加你的业务逻辑
                        
                except json.JSONDecodeError:
                    logger.error(f"无法解析JSON: {event_data}")
            
            # 检查是否达到超时时间
            if asyncio.get_event_loop().time() - start_time > timeout:
                logger.info(f"达到监听超时时间 {timeout} 秒")
                break
                
        # 如果同时启用了WebSocket，可以发送响应
        if sse_client.WS_CLIENT:
            logger.info("通过WebSocket发送响应...")
            websocket = await sse_client.WS_CLIENT
            
            # 发送echo消息
            test_msg = {"action": "echo", "params": {"message": "Hello, SSE client!"}}
            await websocket.send(json.dumps(test_msg))
            
            # 接收响应
            response = await websocket.recv()
            logger.info(f"WebSocket响应: {response}")
            
            # 关闭WebSocket连接
            await websocket.close()
            
    except asyncio.CancelledError:
        logger.info("SSE客户端监听被取消")
    finally:
        # 关闭SSE会话
        if hasattr(sse_client, 'sse_session') and sse_client.sse_session:
            await sse_client.sse_session.close()
            logger.info("SSE客户端会话已关闭")
    
    return "SSE客户端示例完成"

async def websocket_client_example():
    """WebSocket客户端示例"""
    print_section("WebSocket客户端示例")
    
    # 创建WebSocket客户端
    ws_client = NapcatAPI.NapcatWebSocketClient(
        HOST="127.0.0.1",
        PORT=10147,  # WebSocket服务器端口
        TOKEN="your_token_here",  # 可选的认证令牌
        NAME="example_ws_client"
    )
    
    # 连接到WebSocket服务器
    ws_client.WS_CLIENT_CONNECT()
    logger.info(f"WebSocket客户端已准备连接到 {ws_client.host}:{ws_client.port}")
    
    try:
        # 建立WebSocket连接
        websocket = await ws_client.WS_CLIENT
        logger.info("WebSocket连接已建立")
        
        # 发送消息
        test_messages = [
            {"action": "get_status", "params": {}},
            {"action": "get_version", "params": {}},
            {
                "action": "send_private_msg", 
                "params": {
                    "user_id": 123456789,
                    "message": "你好，这是WebSocket测试消息"
                }
            }
        ]
        
        for msg in test_messages:
            # 发送JSON消息
            await websocket.send(json.dumps(msg))
            logger.info(f"已发送: {msg}")
            
            # 等待响应
            response = await websocket.recv()
            logger.info(f"收到响应: {response}")
            
            # 短暂等待，避免消息发送过快
            await asyncio.sleep(1)
            
        # 设置消息监听
        logger.info("开始监听WebSocket消息...")
        timeout = 15  # 15秒超时
        
        try:
            # 设置接收超时
            while True:
                # 接收消息，带超时
                response = await asyncio.wait_for(websocket.recv(), timeout)
                logger.info(f"收到消息: {response}")
                
                # 可选：解析并处理接收到的消息
                try:
                    data = json.loads(response)
                    # 根据消息类型进行处理
                    if "post_type" in data:
                        logger.info(f"收到事件类型: {data['post_type']}")
                        
                        # 如果是私聊消息，可以自动回复
                        if data["post_type"] == "message" and data.get("message_type") == "private":
                            reply = {
                                "action": "send_private_msg",
                                "params": {
                                    "user_id": data["user_id"],
                                    "message": f"你发送了: {data['raw_message']}"
                                }
                            }
                            await websocket.send(json.dumps(reply))
                            logger.info(f"已回复: {reply}")
                except json.JSONDecodeError:
                    logger.warning(f"收到非JSON消息: {response}")
                    
        except asyncio.TimeoutError:
            logger.info(f"监听超时 ({timeout}秒)")
        
    except Exception as e:
        logger.error(f"WebSocket客户端错误: {str(e)}")
    finally:
        # 关闭WebSocket连接
        if ws_client.WS_CLIENT:
            websocket = await ws_client.WS_CLIENT
            await websocket.close()
            logger.info("WebSocket连接已关闭")
    
    return "WebSocket客户端示例完成"

async def http_server_example():
    """HTTP服务器示例"""
    print_section("HTTP服务器示例")
    
    # 创建HTTP服务器
    http_server = NapcatAPI.NapcatHttpServer(
        HOST="127.0.0.1",
        PORT=10143,  # 服务器端口
        TOKEN="your_token_here",  # 可选的认证令牌
        NAME="example_http_server"
    )
    
    # 设置服务器绑定
    http_server.HTTP_SERVER_BINDING()
    logger.info(f"HTTP服务器已绑定到 {http_server.host}:{http_server.port}")
    
    # 注册消息处理函数
    @http_server.HTTP_SERVER.on_event("message")
    async def handle_message(event):
        """处理接收到的消息事件"""
        logger.info(f"收到消息事件: {event}")
        
        # 简单的文本消息回复示例
        if event.get("message_type") == "private":
            # 构建回复消息
            reply = {
                "reply": f"你发送了: {event.get('raw_message', '')}",
                "auto_escape": False  # 是否转义CQ码
            }
            return reply
        
        return None  # 对于不需要回复的消息
    
    # 注册自定义API处理函数
    @http_server.HTTP_SERVER.on_api("custom_api")
    async def handle_custom_api(params):
        """处理自定义API调用"""
        logger.info(f"收到自定义API调用: {params}")
        
        # 返回处理结果
        return {
            "status": "success",
            "data": {
                "message": "这是自定义API的响应",
                "params_received": params
            }
        }
    
    try:
        # 启动HTTP服务器
        await http_server.HTTP_SERVER.start()
        
        # 服务器将持续运行，这里我们让它运行一段时间作为示例
        logger.info("HTTP服务器已启动，将运行60秒...")
        await asyncio.sleep(60)
        
    finally:
        # 关闭HTTP服务器
        await http_server.HTTP_SERVER.stop()
        logger.info("HTTP服务器已关闭")
    
    return "HTTP服务器示例完成"

async def websocket_server_example():
    """WebSocket服务器示例"""
    print_section("WebSocket服务器示例")
    
    # 创建WebSocket服务器
    ws_server = NapcatAPI.NapcatWebSocketServer(
        HOST="127.0.0.1",
        PORT=10145,  # WebSocket服务器端口
        TOKEN="your_token_here",  # 可选的认证令牌
        NAME="example_ws_server"
    )
    
    # 设置WebSocket服务器绑定
    ws_server.WS_SERVER_BINDING()
    logger.info(f"WebSocket服务器已绑定到 {ws_server.host}:{ws_server.port}")
    
    try:
        # 启动WebSocket服务器
        server = ws_server.WS_SERVER
        async with server:
            logger.info("WebSocket服务器已启动，等待连接...")
            
            # 服务器将持续运行，这里我们让它运行一段时间作为示例
            await asyncio.sleep(60)
            
    except Exception as e:
        logger.error(f"WebSocket服务器错误: {str(e)}")
    finally:
        logger.info("WebSocket服务器已关闭")
    
    return "WebSocket服务器示例完成"

# ======== 主程序 ========

async def main():
    """示例主程序"""
    print_section("AIVK-QQ API 示例程序")
    
    # 设置AIVK根目录
    aivk_root = Path.home() / ".aivk"  # 默认路径
    AivkIO.set_aivk_root(aivk_root)
    logger.info(f"设置AIVK根目录为: {aivk_root}")
    
    # 选择要运行的示例
    examples = {
        "1": ("HTTP客户端示例", http_client_example),
        "2": ("HTTP SSE客户端示例", sse_client_example),
        "3": ("WebSocket客户端示例", websocket_client_example),
        "4": ("HTTP服务器示例", http_server_example),
        "5": ("WebSocket服务器示例", websocket_server_example)
    }
    
    # 显示菜单
    print("\n选择要运行的示例:")
    for key, (name, _) in examples.items():
        print(f"{key}: {name}")
    print("0: 退出程序")
    
    choice = input("\n请输入选项 [0-5]: ").strip()
    
    if choice == "0":
        print("退出程序")
        return
    
    if choice in examples:
        name, example_func = examples[choice]
        print(f"\n运行 {name}...")
        
        try:
            result = await example_func()
            print(f"\n{result}")
        except Exception as e:
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("无效的选项!")

if __name__ == "__main__":
    try:
        # 运行异步主程序
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序异常: {str(e)}")