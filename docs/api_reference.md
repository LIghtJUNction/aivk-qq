# API 参考文档

## 消息构建
### 文本消息
```python
from aivk_qq.napcat.message import Message

text_msg = Message.text("Hello World")
```

### 图片消息
```python
image_msg = Message.image("https://example.com/image.jpg")
```

### 复合消息
```python
mixed_msg = Message(
    Message.text("请看图片:"),
    image_msg
)
```

## 消息序列化
### 转换为JSON
```python
msg_json = mixed_msg.json(ensure_ascii=False)
```

### 解析JSON
```python
parsed_msg = Message.parse_raw(msg_json)
```

## MCP服务配置
```python
from aivk_qq.mcp.server import MCPServer

class QQBotServer(MCPServer):
    @tool("send_group_msg")
    async def send_group_message(self, group_id: int, message: str) -> dict:
        return await self.execute_qq_api(
            action="send_group_msg",
            data={"group_id": group_id, "message": message}
        )
