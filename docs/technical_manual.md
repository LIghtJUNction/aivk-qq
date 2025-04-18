# Nacpat(QQ API) SDK 技术手册

## 安装指南

### 环境要求
- Python 3.11+
- UV包管理器 0.1.0+
- 支持MCP协议的服务端

### 安装步骤
```bash
# 安装核心SDK
uv pip install aivk-qq

# 安装开发依赖
uv pip install "aivk-qq[dev]" --python python3.11

# 验证安装
uv run python -c "import aivk_qq; print(aivk_qq.__version__)"
```

### MCP服务配置
```python
from aivk_qq.mcp.server import MCPServer

class QQBotServer(MCPServer):
    @tool("send_group_msg")
    async def send_group_message(self, group_id: int, message: str) -> dict:
        """发送群组消息工具"""
        return await self.execute_qq_api(
            action="send_group_msg",
            data={"group_id": group_id, "message": message}
        )

    @resource("/qq/events")
    async def qq_events(self) -> dict:
        """获取QQ事件流资源"""
        return self.access_qq_event_stream()
```

## 消息构建

### 消息组件使用
```python
from aivk_qq.napcat.message import Message, MessageSegment

# 文本消息
text_msg = Message.text("Hello World")

# 图片消息
image_msg = MessageSegment.image("https://example.com/image.jpg")

# 复合消息
mixed_msg = Message(
    MessageSegment.text("请看图片:"),
    image_msg
)
```

### 消息序列化
```python
# 转换为JSON字符串
msg_json = mixed_msg.json(ensure_ascii=False)

# 从JSON解析
parsed_msg = Message.parse_raw(msg_json)
```

## 架构设计

### 项目结构
```
aivk-qq/
├── src/
│   └── aivk_qq/
│       ├── napcat/          # QQ协议实现核心
│       │   ├── api/         # OpenAPI接口封装
│       │   ├── client/      # 网络客户端(HTTP/WS/SSE)
│       │   ├── events/      # 事件处理系统
│       │   └── utils/       # 工具类(校验/日志/类型)
│       ├── mcp/             # MCP服务器实现
│       │   └── server.py    # MCP服务主模块
│       └── base/            # 基础工具库
├── tests/                   # 测试套件
├── docs/                    # 文档系统
└── examples/                # 使用示例
```

### 模块说明
#### 1. Napcat 核心模块
- **api/** 
  - `actions.py`: API请求构造器
  - `models.py`: 数据模型定义
- **client/**
  - 多协议客户端实现：
    - `http_client.py`: HTTP REST客户端
    - `ws_client.py`: WebSocket实时通信
    - `sse_client.py`: 服务端事件推送

#### 2. MCP 集成层
- `server.py` 提供以下能力：
  - 自动加载MCP工具集
  - 协议转换适配器（QQ API ↔ MCP规范）
  - 服务生命周期管理

#### 3. 事件系统
- 采用发布-订阅模式：
  ```mermaid
  graph LR
  Client-->|接收事件|Dispatcher
  Dispatcher-->|路由事件|Handler[事件处理器]
  Handler-->|响应动作|API
  ```

### 设计原则
1. **分层架构**：网络层→业务层→服务层
2. **协议隔离**：HTTP/WS实现细节封装在client模块
```python
from typing import Any
from unittest import TestCase
from unittest.mock import Mock
from typing_extensions import override

class WSClientTestBase(TestCase):
    @override
    def setUp(self) -> None:
        self.mock_api: Mock = Mock()
        self.client: Any  # 使用具体类型替换Any
        super().setUp()
```

### Mock对象类型注解
```python
from unittest.mock import Mock
from aivk_qq.napcat.client.ws_client import WSClientBase

def test_connection():
    # 正确声明Mock类型
    mock_client: Mock[WSClientBase] = Mock(spec=WSClientBase)
    mock_client.connect.assert_called_once()
```
```python

### 私有方法访问规范
```markdown
- 测试中禁止直接访问`_`开头的保护方法
- 如需测试私有逻辑，应通过公共方法间接测试
- 必要时使用`@visibility("protected")`装饰器
```

## UV测试依赖配置
```bash
# 安装带类型校验的测试环境
uv pip install ".[test]" --python python3.11 -f strict

# 运行类型检查与测试
uv run pyright tests/
uv run pytest tests/ -v --tb=short --strict-markers

# 生成测试覆盖率报告
uv run coverage run -m pytest tests/
uv run coverage xml -o reports/coverage.xml
```

## MCP测试服务集成
```python
from aivk_qq.mcp.server import MCPServer

class TestToolsServer(MCPServer):
    @tool("run_ws_tests")
    async def run_ws_tests(self, output: str = "reports/ws_test.xml") -> dict:
        """通过MCP执行WebSocket测试并生成JUnit报告"""
        return await self.execute(
            "uv run pytest tests/test_ws_client.py -v --junitxml=" + output
        )

    @resource("/reports/coverage")
    async def get_coverage(self) -> dict:
        """获取最新测试覆盖率数据"""
        return self.access_file("reports/coverage.xml")
```
