"""
使用模块化后的Napcat客户端示例

展示如何使用重构后的Napcat模块创建客户端、处理事件和发送消息
"""

import asyncio
from typing import Dict, Any

from aivk_qq.napcat import NapcatClient, Message, set_log_level
from aivk_qq.base.enums import PostType

# 设置日志级别
set_log_level("DEBUG")

async def main():
    # 创建WebSocket客户端
    client = NapcatClient.WS_CLIENT(
        host="127.0.0.1",
        port=6700,
        ws_path="/",
        token=None,  # 如果你的服务需要token，请在这里提供
        name="ExampleClient",
        msgtype="Array"
    )
    
    # 设置默认机器人QQ号（可选）
    client.set_default_self_id(123456789)
    
    # 注册私聊消息处理器
    @client.on_message("private")
    async def handle_private_message(event: Dict[str, Any]) -> None:
        """处理私聊消息"""
        # 提取信息
        sender_id = event.get("user_id")
        raw_message = event.get("raw_message", "")
        
        print(f"收到私聊消息 [{sender_id}]: {raw_message}")
        
        # 创建回复消息
        reply = Message().text(f"你发送了: {raw_message}").face(101)
        
        # 发送回复消息
        await client.send_private_msg(user_id=sender_id, message=reply)
        
    # 注册群聊消息处理器
    @client.on_message("group")
    async def handle_group_message(event: Dict[str, Any]) -> None:
        """处理群聊消息"""
        # 提取信息
        group_id = event.get("group_id")
        sender_id = event.get("user_id")
        raw_message = event.get("raw_message", "")
        
        print(f"收到群消息 [{group_id}] [{sender_id}]: {raw_message}")
        
        # 只响应@自己的消息或包含特定关键词的消息
        if "[CQ:at,qq=" in raw_message or "你好" in raw_message:
            # 创建回复消息
            reply = Message().at(sender_id).text(" 你好！").face(101)
            
            # 发送群回复
            await client.send_group_msg(group_id=group_id, message=reply)
    
    # 通用事件处理器
    @client.on()
    async def handle_all_events(event: Dict[str, Any]) -> None:
        """处理所有事件类型（调试用）"""
        post_type = event.get("post_type")
        
        # 跳过已经专门处理的消息事件
        if post_type == PostType.MESSAGE:
            return
            
        # 记录其他类型事件
        print(f"收到事件: {post_type}")
    
    # 启动客户端
    print("正在启动客户端...")
    await client.start()
    
    try:
        # 持续运行直到被中断
        print("客户端已启动，按Ctrl+C停止")
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        # 确保正确关闭客户端
        print("正在关闭客户端...")
        await client.stop()

if __name__ == "__main__":
    asyncio.run(main())