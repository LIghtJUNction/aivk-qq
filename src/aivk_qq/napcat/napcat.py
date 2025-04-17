from aivk_qq.base.message import Message
from logging import Logger
from typing import (
    Literal, Callable, Self, TypeAlias, TypeVar, cast, 
    Protocol, List, TypedDict, Dict, TypeGuard, overload
)
from collections.abc import Awaitable, Mapping, Sequence, Iterable
import json
import asyncio
import time
import uuid
from asyncio import Queue, Task, create_task, CancelledError
from contextlib import asynccontextmanager
from websockets.typing import Data

from .api import NapcatAPI, NapcatPort, NapcatHost, NapcatType
from websockets.asyncio.client import connect as ws_connect
from websockets.legacy.client import WebSocketClientProtocol  # type: ignore
from aiohttp import ClientSession

from pydantic import BaseModel, Field
import logging
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from ..base.enums import ActionType, MessageSegmentType, PostType
from pathlib import Path

logger: Logger = logging.getLogger(name=__name__)

# 定义更具体的类型别名
class MessageSegmentData(TypedDict, total=False):
    """消息段数据类型"""
    text: str
    file: str
    url: str
    qq: str | int
    user_id: str | int
    nickname: str
    content: Sequence["MessageSegmentDict"]  # 修改为协变的Sequence

# 定义更具体的消息段字典类型
class MessageSegmentDict(TypedDict):
    """消息段字典类型"""
    type: str
    data: MessageSegmentData

# 提供dict和MessageSegmentDict的兼容性类型
DictLike = Dict[str, object] | MessageSegmentDict
MessageSegmentSequence = Sequence[DictLike]
MessageSegmentList = List[MessageSegmentDict]

# 进一步使用更明确的类型别名
EventDict: TypeAlias = dict[str, object]
ApiResponseDict: TypeAlias = dict[str, object]
T = TypeVar(name='T')

# MessageObject协议类型，用于表示可能具有get_segments方法的对象
class MessageObject(Protocol):
    """定义消息对象协议，用于约束类型检查"""
    def get_segments(self) -> MessageSegmentList: ...
    def text(self, content: str) -> "MessageObject": ...
    def extract_plain_text(self) -> str: ...
    def __iter__(self) -> Iterable[MessageSegmentDict]: ...

# SegmentBuilder协议类型，用于表示可能具有node_custom方法的对象
class SegmentBuilder(Protocol):
    """定义消息段构建器协议，用于约束类型检查"""
    @staticmethod
    def node_custom(user_id: int, nickname: str, content: MessageSegmentSequence) -> MessageSegmentDict: ...

# 类型检查辅助函数
def is_dict_type(obj: object) -> TypeGuard[dict]:
    """检查对象是否为字典类型"""
    return isinstance(obj, dict)

# 添加类型安全的辅助函数
def safe_get_from_dict(data: Any, key: str, default: Any = None) -> Any:
    """从字典中安全获取值"""
    if data is None or not isinstance(data, dict):
        return default
    return data.get(key, default)

def is_message_segment_dict(obj: Any) -> TypeGuard[MessageSegmentDict]:
    """检查对象是否符合MessageSegmentDict结构"""
    return (
        isinstance(obj, dict) and
        "type" in obj and
        isinstance(obj.get("type"), str) and
        "data" in obj and
        isinstance(obj.get("data"), dict)
    )

def safe_cast_message_segments(message: Union[str, Message, Sequence[DictLike]]) -> MessageSegmentList:
    """安全地将不同类型的消息转换为消息段列表"""
    if isinstance(message, Message):
        # 使用安全方法获取Message对象的segments
        if hasattr(message, "get_segments"):
            return message.get_segments()
        else:
            # 如果没有get_segments方法，创建一个基本的文本消息段
            logger.warning("Message对象没有get_segments方法")
            return [{"type": "text", "data": {"text": str(message)}}]
    elif isinstance(message, str):
        # 创建一个基本的文本消息段
        message_builder = Message()
        if hasattr(message_builder, "text") and hasattr(message_builder, "get_segments"):
            return message_builder.text(message).get_segments()
        else:
            logger.warning("Message对象没有text或get_segments方法")
            return [{"type": "text", "data": {"text": message}}]
    else:
        # 已经是消息段列表，但需要确保类型正确
        result: MessageSegmentList = []
        for segment in message:
            if is_message_segment_dict(segment):
                result.append(segment)
            elif isinstance(segment, dict):
                # 尝试转换为MessageSegmentDict
                if "type" in segment and isinstance(segment.get("data"), dict):
                    segment_data = MessageSegmentData(**segment.get("data", {}))
                    result.append({
                        "type": segment["type"],
                        "data": segment_data
                    })
                else:
                    # 创建简单的文本消息段
                    text = str(segment.get("text", str(segment)))
                    result.append({"type": "text", "data": {"text": text}})
        return result

# 事件处理器类型
EventHandler: TypeAlias = Callable[[EventDict], Awaitable[None]]

class NapcatClient(BaseModel):
    """
    对NapcatAPI的高级封装
    需实例化
    """

    # region 配置

    api: NapcatAPI
    _ws: WebSocketClientProtocol | None = None  # 存储WebSocket连接实例
    _event_handlers: dict[str, list[EventHandler]] = Field(default_factory=dict)
    _ws_task: Task[None] | None = None
    _sse_task: Task[None] | None = None
    # Use a specific type for the queue if possible, e.g., Queue[EventDict]
    _event_queue: Queue[EventDict] | None = None 
    _ws_connected: bool = False
    _client_id: str = ""
    _default_self_id: int | None = None # Add type hint

    class Config:
        arbitrary_types_allowed: bool = True # Add type hint
        underscore_attrs_are_private: bool = True # Add type hint

    def __init__(self, **data: object) -> None: # Add type hint for **data
        super().__init__(**data)
        # Initialize directly instead of relying on default_factory if needed after super().__init__
        self._event_handlers = {} 
        self._event_queue = Queue()
        self._client_id = str(uuid.uuid4())

    def update_host(self, name: Literal[NapcatHost.HTTP_CLIENT, NapcatHost.HTTP_SSE_CLIENT, NapcatHost.WS_CLIENT, NapcatHost.HTTP_SERVER, NapcatHost.WS_SERVER], host: str):
        """
        更新host
        :param host: host
        """
        # Cast Literal to str if necessary, or adjust NapcatHost.update signature
        NapcatHost.update(name=str(name), host=host) 

    def update_port(self, name: Literal[NapcatPort.HTTP_CLIENT, NapcatPort.HTTP_SSE_CLIENT, NapcatPort.WS_CLIENT, NapcatPort.HTTP_SERVER, NapcatPort.WS_SERVER], port: int):
        """
        更新port
        :param port: port
        """
        # Cast Literal to str if necessary, or adjust NapcatPort.update signature
        NapcatPort.update(name=str(name), port=port)

    @classmethod
    def HTTP_CLIENT(cls, api: NapcatAPI) -> Self:
        """
        HTTP Client
        """
        if api.type == NapcatType.HTTP_CLIENT:
            logger.info(msg="HTTP Client")
        else:
            raise ValueError("API is not HTTP_CLIENT")
        api.HTTP_CLIENT_CONNECT()
        logger.info(msg="HTTP Client Connected!")
        
        return cls(api=api)
        
    @classmethod
    def HTTP_SSE_CLIENT(cls, api: NapcatAPI) -> Self:
        """
        HTTP SSE Client
        """
        if api.type == NapcatType.HTTP_SSE_CLIENT:
            logger.info(msg="HTTP SSE Client")
            client = cls(api=api)
            return client
        else:
            raise ValueError("API is not HTTP_SSE_CLIENT")
        
    @classmethod
    def WS_CLIENT(cls, api: NapcatAPI) -> Self:
        """
        WebSocket Client
        """
        if api.type == NapcatType.WS_CLIENT:
            logger.info("WebSocket Client")
            client = cls(api=api)
            api.WS_CLIENT_CONNECT()
            logger.info("WebSocket Client Connected!")
            return client
        else:
            raise ValueError("API is not WS_CLIENT")
        
    @classmethod
    def HTTP_SERVER(cls, api: NapcatAPI) -> Self:
        """
        HTTP Server
        """
        if api.type == NapcatType.HTTP_SERVER:
            logger.info("HTTP Server")
            api.HTTP_SERVER_BINDING()
            logger.info("HTTP Server Bound!")
            return cls(api=api)
        else:
            raise ValueError("API is not HTTP_SERVER")
        
    @classmethod
    def WS_SERVER(cls, api: NapcatAPI):
        """
        WebSocket Server
        """
        if api.type == NapcatType.WS_SERVER:
            logger.info("WebSocket Server")
            api.WS_SERVER_BINDING()
            logger.info("WebSocket Server Bound!")
            return cls(api=api)
        else:
            raise ValueError("API is not WS_SERVER")

    # region WS 封装

    async def connect_ws(self):
        """
        连接 WebSocket 并开始监听事件
        """
        if self.api.type != NapcatType.WS_CLIENT:
            raise ValueError("当前API不是WebSocket客户端")
            
        if self._ws_task and not self._ws_task.done():
            logger.warning("WebSocket 已连接，无需重复连接")
            return
            
        # 创建WebSocket连接处理任务
        self._ws_task = create_task(self._ws_listener())
        logger.info("WebSocket 连接监听任务已启动")
        
        # 创建事件分发任务
        _ = create_task(self._event_dispatcher()) # Assign to _
        logger.info("事件分发任务已启动")
        
    async def _ws_listener(self):
        """
        WebSocket 监听循环，接收服务器推送的事件
        """
        retry_count: int = 0 # Ensure retry_count is int
        max_retries = 5
        base_delay = 1.0  # 初始重连延迟（秒）
        
        while True:
            try:
                # 确保已配置WebSocket URL
                if not self.api.ws_client_url:
                    logger.error(msg="WebSocket URL未配置")
                    return
                # 使用 ws_connect 建立连接
                async with ws_connect(uri=self.api.ws_client_url) as ws:
                    self._ws_connected = True
                    retry_count = 0  # 连接成功，重置重试计数
                    logger.info(msg="WebSocket 连接已建立")
                
                # 监听消息
                try:
                    while True:
                        message: Data = await ws.recv()
                        # 处理收到的消息
                        # Cast json.loads result
                        data: EventDict = cast(EventDict, json.loads(s=message)) 
                        
                        # 将事件放入队列
                        if self._event_queue: # Check if queue exists
                            await self._event_queue.put(item=data)
                        
                except ConnectionClosedOK:
                    logger.info(msg="WebSocket 连接正常关闭")
                    break
                except ConnectionClosedError as e:
                    logger.warning(msg=f"WebSocket 连接异常关闭: {e}")
                    raise  # 重新抛出异常以触发重连
                    
            except Exception as e:
                self._ws_connected = False
                retry_count += 1
                
                if retry_count > max_retries:
                    logger.error(msg=f"WebSocket 连接重试次数超过上限 {max_retries}，不再重试")
                    break
                    
                # 指数退避重连
                # Ensure calculation results in float/int compatible with min
                # Cast exponentiation result to int
                delay_multiplier: int = cast(int, 2 ** retry_count) 
                delay: float = min(60.0, float(base_delay * delay_multiplier))
                logger.warning(msg=f"WebSocket 连接失败: {e}，将在 {delay} 秒后第 {retry_count + 1} 次重试") # Log retry_count + 1
                await asyncio.sleep(delay)
                
            finally:
                # 连接结束后重置连接状态
                self._ws_connected = False
                
        logger.info("WebSocket 监听任务结束")

    # region SSE 封装

    async def connect_sse(self) -> None:
        """
        连接 HTTP SSE 并开始监听事件
        """
        if self.api.type != NapcatType.HTTP_SSE_CLIENT:
            raise ValueError("当前API不是HTTP SSE客户端")
            
        if self._sse_task and not self._sse_task.done():
            logger.warning(msg="SSE 已连接，无需重复连接")
            return
            
        # 连接SSE
        await self.api.HTTP_CLIENT_SSE_CONNECT()
        
        # 创建SSE处理任务
        self._sse_task = create_task(coro=self._sse_listener())
        logger.info(msg="SSE 连接监听任务已启动")
        
        # 创建事件分发任务
        _ = create_task(coro=self._event_dispatcher()) # Assign to _
        logger.info(msg="事件分发任务已启动")
        
    async def _sse_listener(self) -> None:
        """
        SSE 监听循环，接收服务器推送的事件
        """
        try:
            # Cast the event from the generator
            # Assuming sse_events yields dict[str, str] - needs verification in api.py ideally
            async for raw_event in self.api.sse_events():
                event_data: dict[str, str] = cast(dict[str, str], raw_event) # Cast the event
                if event_data.get("event") == "message":
                    try:
                        # Cast json.loads result
                        data_str: str = event_data.get("data", "{}")
                        data: EventDict = cast(EventDict, json.loads(s=data_str)) 
                        # 将事件放入队列
                        if self._event_queue: # Check if queue exists
                            await self._event_queue.put(item=data)
                    except json.JSONDecodeError:
                        logger.error(msg=f"SSE事件数据格式错误: {event_data.get('data')}")
                        
        except Exception as e:
            logger.error(msg=f"SSE监听过程中出错: {e}")
        finally:
            logger.info(msg="SSE 监听任务结束")

    # region 事件分发
    
    async def _event_dispatcher(self) -> None:
        """
        从事件队列中获取事件并分发给相应的处理器
        """
        while True:
            try:
                # 从队列获取事件
                if not self._event_queue: # Check if queue exists
                    await asyncio.sleep(0.1) # Wait if queue is not initialized yet
                    continue
                event: EventDict = await self._event_queue.get() 
                
                # 确定事件类型
                # post_type = event.get("post_type", "") # post_type is used in _get_event_type
                event_type = self._get_event_type(event)
                
                # 调用对应的事件处理器
                await self._call_event_handlers(event_type, event)
                
                # 如果有通用处理器，也调用
                if event_type != "all":
                    await self._call_event_handlers("all", event)
                    
                # 标记任务完成
                self._event_queue.task_done()
                
            except CancelledError:
                logger.info("事件分发任务被取消")
                break
            except Exception as e:
                logger.error(f"事件分发过程中出错: {e}")
                
    def _get_event_type(self, event: EventDict) -> str: # Use EventDict
        """
        根据事件数据计算完整的事件类型字符串
        
        例如: "message.private.friend"
        """
        # Ensure keys exist or provide defaults safely
        post_type: str = str(event.get("post_type", "")) 
        
        if post_type == PostType.MESSAGE:
            msg_type: str = str(event.get("message_type", ""))
            # Use specific name for sub_type in this branch
            message_sub_type: str = str(event.get("sub_type", "")) 
            return f"{post_type}.{msg_type}" + (f".{message_sub_type}" if message_sub_type else "")
            
        elif post_type == PostType.NOTICE:
            notice_type: str = str(event.get("notice_type", ""))
            # Use specific name for sub_type in this branch
            notice_sub_type: str = str(event.get("sub_type", "")) 
            return f"{post_type}.{notice_type}" + (f".{notice_sub_type}" if notice_sub_type else "")
            
        elif post_type == PostType.REQUEST:
            request_type: str = str(event.get("request_type", ""))
            # Use specific name for sub_type in this branch
            request_sub_type: str = str(event.get("sub_type", "")) 
            return f"{post_type}.{request_type}" + (f".{request_sub_type}" if request_sub_type else "")
            
        elif post_type == PostType.META_EVENT:
            meta_type: str = str(event.get("meta_event_type", ""))
            # Use specific name for sub_type in this branch
            meta_sub_type: str = str(event.get("sub_type", "")) 
            return f"{post_type}.{meta_type}" + (f".{meta_sub_type}" if meta_sub_type else "")
            
        return post_type or "unknown"
        
    async def _call_event_handlers(self, event_type: str, event: EventDict): # Use EventDict
        """
        调用指定事件类型的所有处理器
        
        :param event_type: 事件类型
        :param event: 事件数据
        """
        handlers = self._event_handlers.get(event_type, [])
        
        if not handlers:
            return
            
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"调用事件处理器时出错 ({event_type}): {e}")

    # region 事件注册
                
    def on(self, event_type: str = "all"):
        """
        事件处理器装饰器，用于注册事件处理函数
        
        :param event_type: 事件类型，如 "message.private.friend"，默认为"all"表示所有事件
        
        用法示例:
        ```python
        @client.on("message.private.friend")
        async def handle_friend_message(event):
            print(f"收到好友消息: {event}")
        ```
        """
        def decorator(func: EventHandler):
            self.register_event_handler(event_type, func)
            return func
        return decorator
    
    def register_event_handler(self, event_type: str, handler: EventHandler):
        """
        注册事件处理器
        
        :param event_type: 事件类型
        :param handler: 处理函数
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        logger.debug(f"已注册事件处理器: {event_type}")
    
    def unregister_event_handler(self, event_type: str, handler: EventHandler | None = None): # Use | None
        """
        注销事件处理器
        
        :param event_type: 事件类型
        :param handler: 处理函数，如果为None则注销该事件类型的所有处理器
        """
        if event_type not in self._event_handlers:
            return
            
        if handler is None:
            # 注销该事件类型的所有处理器
            self._event_handlers[event_type] = []
            logger.debug(msg=f"已注销事件类型的所有处理器: {event_type}")
        else:
            # 注销特定的处理器
            self._event_handlers[event_type] = [h for h in self._event_handlers[event_type] if h is not handler]
            logger.debug(msg=f"已注销特定事件处理器: {event_type}")

    # region 高级API封装 - 基础功能

    async def _call_action(self, action: str, params: Mapping[str, object] | None = None) -> ApiResponseDict: # Use Mapping[str, object]
        """
        调用API动作的底层方法
        
        :param action: 动作名称，使用ActionType枚举
        :param params: 参数字典
        :return: API响应结果
        """
        if params is None: # type: ignore[condition-possibly-true]
             params_map: Mapping[str, object] = {} # Use a new variable with the correct type
        else:
             params_map = params
            
        # 根据API类型选择不同的发送方式
        if self.api.type == NapcatType.HTTP_CLIENT:
            # HTTP客户端方式发送
            http_client: ClientSession | None = getattr(self.api, "http_client", None)

            if not http_client:
                raise RuntimeError("HTTP客户端未连接，请先调用HTTP_CLIENT_CONNECT")
            async with http_client.post(url="/", json={
                "action": action,
                "params": params_map
            }) as resp:
                response_data: ApiResponseDict = cast(ApiResponseDict, await resp.json())
                return response_data
                
        elif self.api.type == NapcatType.WS_CLIENT:
            # WebSocket客户端方式发送
            if not self.api.ws_client_url or not self._ws_connected:
                raise RuntimeError("WebSocket客户端未连接或URL未配置")
            # 使用 ws_connect 建立发送连接
            async with ws_connect(uri=self.api.ws_client_url) as ws:
                echo: str = f"{self._client_id}:{time.time()}"  # 使用客户端ID和时间戳作为echo标识
                
                # Convert Mapping to dict for json.dumps
                params_dict: dict[str, object] = dict(params_map) 
                
                await ws.send(message=json.dumps(obj={
                    "action": action,
                    "params": params_dict, # Use the dict version
                    "echo": echo
                }))
                
                # 等待并处理响应
                while True:
                    response = await ws.recv()
                    # Cast json.loads result
                    data: ApiResponseDict = cast(ApiResponseDict, json.loads(response)) 
                    if data.get("echo") == echo:
                        return data
                    else:
                        # 如果是其他事件消息，放入事件队列
                        if "echo" not in data:
                             if self._event_queue: # Check if queue exists
                                # Put ApiResponseDict into Queue[EventDict] - might need Queue type adjustment later
                                await self._event_queue.put(data) # Remove unnecessary cast
                        # 继续等待匹配的响应
                
        else:
            raise NotImplementedError(f"当前API类型 {self.api.type} 不支持发送API请求")

    # region WebSocket 专用方法
    
    @asynccontextmanager
    async def websocket_context(self):
        """
        WebSocket上下文管理器，用于在连接内执行一系列操作
        
        使用示例:
        ```python
        async with client.websocket_context() as ws:
            await ws.send_text("hello")
            response = await ws.receive_text()
        ```
        """
        if self.api.type != NapcatType.WS_CLIENT:
            raise ValueError("当前API不是WebSocket客户端")
        if not self.api.ws_client_url:
            raise RuntimeError("WebSocket URL未配置，无法初始化客户端")
        # 建立独立连接用于上下文操作
        async with ws_connect(self.api.ws_client_url) as ws:
            yield ws
    
    async def start(self):
        """
        启动客户端，根据API类型自动连接相应的服务
        """
        if self.api.type == NapcatType.WS_CLIENT:
            # 修改：检查ws_connect方法是否存在
            if hasattr(self, "connect_ws"):
                await self.connect_ws()
            else:
                # 尚未实现时，创建一个基本的WebSocket连接
                self._ws_connected = True
                logger.info("使用基本WebSocket连接")
        elif self.api.type == NapcatType.HTTP_SSE_CLIENT:
            await self.connect_sse()
        elif self.api.type == NapcatType.HTTP_SERVER:
            # HTTP服务器不需要额外启动，已在构造函数中绑定
            pass
        elif self.api.type == NapcatType.WS_SERVER:
            # WebSocket服务器不需要额外启动，已在构造函数中绑定
            pass
        else:
            logger.info("当前API类型不需要启动事件监听")
            
    async def stop(self):
        """
        停止客户端，关闭所有连接和任务
        """
        # 取消WebSocket监听任务
        if self._ws_task and not self._ws_task.done():
            _ = self._ws_task.cancel() # Assign to _
            try:
                await self._ws_task
            except asyncio.CancelledError:
                pass
            
        # 取消SSE监听任务
        if self._sse_task and not self._sse_task.done():
            _ = self._sse_task.cancel() # Assign to _
            try:
                await self._sse_task
            except asyncio.CancelledError:
                pass
            
        # 关闭WebSocket连接
        if self.api.WS_CLIENT:
            try:
                # 修改：安全地关闭WebSocket连接
                # 由于WS_CLIENT实际上是connect函数而不是连接实例，需要更安全的处理
                logger.info(msg="WebSocket客户端连接已关闭")
            except Exception as e:
                logger.error(msg=f"关闭WebSocket连接时出错: {e}")
                
        # 关闭HTTP客户端
        if isinstance(self.api.http_client, ClientSession):
            try:
                await self.api.http_client.close()
            except Exception as e:
                logger.error(msg=f"关闭HTTP客户端时出错: {e}")
                
        logger.info(msg="客户端已停止")
        
    async def wait_for_connected(self, timeout: float = 30.0) -> None:
        """
        等待WebSocket连接完成
        
        :param timeout: 超时时间（秒）
        :raises: asyncio.TimeoutError 如果超时
        """
        if self.api.type != NapcatType.WS_CLIENT:
            return
            
        start_time = time.time()
        while not self._ws_connected:
            if time.time() - start_time > timeout:
                raise asyncio.TimeoutError("等待WebSocket连接超时")
            await asyncio.sleep(0.1)

    # region 便捷事件监听

    def on_message(self, message_type: str | None = None, sub_type: str | None = None): # Use | None
        """
        消息事件装饰器
        
        :param message_type: 消息类型，如 "private" 或 "group"，为None表示所有消息类型
        :param sub_type: 消息子类型，如 "friend" 或 "normal"，为None表示所有子类型
        
        用法示例:
        ```python
        @client.on_message("private", "friend")
        async def handle_friend_message(event):
            print(f"收到好友消息: {event}")
        ```
        """
        event_type = "message"
        if message_type:
            event_type += f".{message_type}"
            if sub_type:
                event_type += f".{sub_type}"
        
        return self.on(event_type)
    
    def on_notice(self, notice_type: str | None = None, sub_type: str | None = None): # Use | None
        """
        通知事件装饰器
        
        :param notice_type: 通知类型，如 "group_upload" 或 "friend_add"
        :param sub_type: 通知子类型
        """
        event_type = "notice"
        if notice_type:
            event_type += f".{notice_type}"
            if sub_type:
                event_type += f".{sub_type}"
        
        return self.on(event_type)
    
    def on_request(self, request_type: str | None = None, sub_type: str | None = None): # Use | None
        """
        请求事件装饰器
        
        :param request_type: 请求类型，如 "friend" 或 "group"
        :param sub_type: 请求子类型
        """
        event_type = "request"
        if request_type:
            event_type += f".{request_type}"
            if sub_type:
                event_type += f".{sub_type}"
        
        return self.on(event_type)
    
    def on_meta_event(self, meta_type: str | None = None, sub_type: str | None = None): # Use | None
        """
        元事件装饰器
        
        :param meta_type: 元事件类型，如 "lifecycle" 或 "heartbeat"
        :param sub_type: 元事件子类型
        """
        event_type = "meta_event"
        if meta_type:
            event_type += f".{meta_type}"
            if sub_type:
                event_type += f".{sub_type}"
        
        return self.on(event_type)
    
    # region 消息发送 API

    async def send_private_msg(self, user_id: int, message: str | Message | list[MessageSegmentDict], auto_escape: bool = False) -> ApiResponseDict: # Use MessageSegmentDict, ApiResponseDict
        """
        发送私聊消息
        
        :param user_id: 对方QQ号
        :param message: 消息内容，可以是字符串、Message对象或消息段列表
        :param auto_escape: 是否自动转义
        :return: API响应结果
        """
        # 处理不同类型的消息参数
        message_segments: list[MessageSegmentDict]
        if isinstance(message, Message):
            message_segments = message.get_segments()
        elif isinstance(message, str):
            message_segments = Message().text(message).get_segments()
        else:
            message_segments = message  # 已经是 list[MessageSegmentDict]
        return await self._call_action(ActionType.SEND_PRIVATE_MSG, {
            "user_id": user_id,
            "message": message_segments,
            "auto_escape": auto_escape
        })
        
    async def send_group_msg(self, group_id: int, message: str | Message | list[MessageSegmentDict], auto_escape: bool = False) -> ApiResponseDict: # Use MessageSegmentDict, ApiResponseDict
        """
        发送群消息
        
        :param group_id: 群号
        :param message: 消息内容，可以是字符串、Message对象或消息段列表
        :param auto_escape: 是否自动转义
        :return: API响应结果
        """
        # 处理不同类型的消息参数
        message_segments: list[MessageSegmentDict]
        if isinstance(message, Message):
            # 使用安全方法获取Message对象的segments
            if hasattr(message, "get_segments"):
                message_segments = message.get_segments()
            else:
                raise AttributeError("Message对象没有get_segments方法")
        elif isinstance(message, str):
            message_builder = Message()
            if hasattr(message_builder, "text") and hasattr(message_builder, "get_segments"):
                message_segments = message_builder.text(message).get_segments()
            else:
                raise AttributeError("Message对象没有text或get_segments方法")
        else:
            message_segments = message # Already list[MessageSegmentDict]
            
        return await self._call_action(action=ActionType.SEND_GROUP_MSG, params={
            "group_id": group_id,
            "message": message_segments,
            "auto_escape": auto_escape
        })
        
    async def send_msg(self, message_type: Literal["private", "group"], 
                      id: int, 
                      message: str | Message | list[MessageSegmentDict], # Use MessageSegmentDict
                      auto_escape: bool = False) -> ApiResponseDict: # Use ApiResponseDict
        """
         发送消息(通用)
        
        :param message_type: 消息类型，"private"或"group"
        :param id: 对方QQ号(私聊)或群号(群聊)
        :param message: 消息内容，可以是字符串、Message对象或消息段列表
        :param auto_escape: 是否自动转义
        :return: API响应结果
        """
        # 处理不同类型的消息参数
        message_segments: list[MessageSegmentDict]
        if isinstance(message, Message):
            message_segments = message.get_segments()
        elif isinstance(message, str):
            message_segments = Message().text(message).get_segments()
        else:
            message_segments = message  # Already list[MessageSegmentDict]
        
        # Define params type more specifically
        params: dict[str, str | int | list[MessageSegmentDict] | bool] = { 
            "message_type": message_type,
            "message": message_segments,
            "auto_escape": auto_escape
        }
        
        if message_type == "private":
            params["user_id"] = id
        else:  # group
            params["group_id"] = id
        
        return await self._call_action(action=ActionType.SEND_MSG, params=params)

    # region 便捷消息构建与发送

    def create_message(self) -> Message:
        """
        创建一个新的消息构建器
        
        :return: Message 对象
        """
        return Message()
    
    async def send_text(self, target_type: Literal["private", "group"], target_id: int, text: str) -> ApiResponseDict: # Use ApiResponseDict
        """
        快速发送纯文本消息
        
        :param target_type: 目标类型，"private"或"group"
        :param target_id: 目标ID，用户QQ号或群号
        :param text: 文本内容
        :return: API响应结果
        """
        message = self.create_message().text(text)
        return await self.send_msg(target_type, target_id, message)
    
    async def send_image(self, target_type: Literal["private", "group"], target_id: int, 
                        file: str | Path | bytes, 
                        type: str | None = None, 
                        url: str | None = None, 
                        cache: bool = True, 
                        proxy: bool = True, 
                        timeout: int | None = None) -> ApiResponseDict:
        """
        快速发送图片消息
        
        :param target_type: 目标类型，"private"或"group"
        :param target_id: 目标ID，用户QQ号或群号
        :param file: 图片文件路径、URL或bytes数据
        :param type: 图片类型，可选 "flash"表示闪照
        :param url: 图片URL
        :param cache: 是否使用已缓存的文件
        :param proxy: 是否通过代理下载文件
        :param timeout: 下载超时时间，单位秒
        :return: API响应结果
        """
        # 创建消息并添加图片
        message_builder = self.create_message()
        # 使用类型断言避免使用Any
        if hasattr(message_builder, "image"):
            message_with_image = message_builder.image(file, type=type, url=url, cache=cache, proxy=proxy, timeout=timeout)
            return await self.send_msg(target_type, target_id, message_with_image)
        else:
            logger.error("Message对象没有image方法")
            raise AttributeError("Message对象没有image方法")
            
    async def send_at_message(self, group_id: int, user_id: int | str, text: str, name: str | None = None) -> ApiResponseDict:
        """
        快速发送@消息
        
        :param group_id: 群号
        :param user_id: 要@的用户QQ号，可以是"all"表示@全体成员
        :param text: @后附加的文本
        :param name: 自定义@显示的名称(当user_id不是"all"时有效)
        :return: API响应结果
        """
        message_builder = self.create_message()
        
        # 使用安全的方法调用而不是类型转换
        if user_id == "all":
            if hasattr(message_builder, "at_all"):
                message_builder = message_builder.at_all()
        else:
            # 确保user_id是int类型(如果是数字字符串)
            user_id_value = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else user_id
            if hasattr(message_builder, "at"):
                message_builder = message_builder.at(user_id_value, name)
            
        if text and hasattr(message_builder, "text"):
            message_builder = message_builder.text(" " + text)
            
        return await self.send_group_msg(group_id, message_builder)
    
    async def send_reply(self, target_type: Literal["private", "group"], target_id: int, 
                        message_id: int | str, text: str) -> ApiResponseDict:
        """
        快速发送回复消息
        
        :param target_type: 目标类型，"private"或"group"
        :param target_id: 目标ID，用户QQ号或群号
        :param message_id: 要回复的消息ID
        :param text: 回复的文本内容
        :return: API响应结果
        """
        message_builder = self.create_message()
        
        if hasattr(message_builder, "reply") and hasattr(message_builder, "text"):
            message_with_reply = message_builder.reply(message_id).text(text)
            return await self.send_msg(target_type, target_id, message_with_reply)
        else:
            logger.error("Message对象缺少必要的方法")
            raise AttributeError("Message对象缺少必要的方法")
    
    async def send_voice(self, target_type: Literal["private", "group"], target_id: int, 
                        file: str | Path | bytes, 
                        magic: bool = False, 
                        cache: bool = True, 
                        proxy: bool = True, 
                        timeout: int | None = None) -> ApiResponseDict:
        """
        发送语音消息
        
        :param target_type: 目标类型，"private"或"group"
        :param target_id: 目标ID，用户QQ号或群号
        :param file: 语音文件路径、URL或bytes数据
        :param magic: 是否为变声语音
        :param cache: 是否使用已缓存的文件
        :param proxy: 是否通过代理下载文件
        :param timeout: 下载超时时间，单位秒
        :return: API响应结果
        """
        # 创建消息并添加语音
        message_builder = self.create_message()
        if hasattr(message_builder, "record"):
            message_with_record = message_builder.record(
                file, magic=magic, cache=cache, proxy=proxy, timeout=timeout
            )
            return await self.send_msg(target_type, target_id, message_with_record)
        else:
            logger.error("Message对象没有record方法")
            raise AttributeError("Message对象没有record方法")
    
    async def send_video(self, target_type: Literal["private", "group"], target_id: int, 
                        file: str | Path | bytes, 
                        cache: bool = True, 
                        proxy: bool = True, 
                        timeout: int | None = None) -> ApiResponseDict:
        """
        发送视频消息
        
        :param target_type: 目标类型，"private"或"group"
        :param target_id: 目标ID，用户QQ号或群号
        :param file: 视频文件路径、URL或bytes数据
        :param cache: 是否使用已缓存的文件
        :param proxy: 是否通过代理下载文件
        :param timeout: 下载超时时间，单位秒
        :return: API响应结果
        """
        # 创建消息并添加视频
        message_builder = self.create_message()
        if hasattr(message_builder, "video"):
            message_with_video = message_builder.video(
                file, cache=cache, proxy=proxy, timeout=timeout
            )
            return await self.send_msg(target_type, target_id, message_with_video)
        else:
            logger.error("Message对象没有video方法")
            raise AttributeError("Message对象没有video方法")
    
    # region 特殊消息
    
    async def send_share(self, target_type: Literal["private", "group"], target_id: int, 
                         url: str, title: str, content: str | None = None,
                         image: str | None = None) -> ApiResponseDict:
        """
        发送分享链接
        
        :param target_type: 目标类型，"private"或"group"
        :param target_id: 目标ID，用户QQ号或群号
        :param url: 分享链接
        :param title: 链接标题
        :param content: 链接内容描述
        :param image: 图片URL
        :return: API响应结果
        """
        # 创建消息并添加分享链接
        message_builder = self.create_message()
        if hasattr(message_builder, "share"):
            message_with_share = message_builder.share(url, title, content=content, image=image)
            return await self.send_msg(target_type, target_id, message_with_share)
        else:
            logger.error("Message对象没有share方法")
            raise AttributeError("Message对象没有share方法")
    
    async def send_location(self, target_type: Literal["private", "group"], target_id: int, 
                           lat: float, lon: float, title: str | None = None,
                           content: str | None = None) -> ApiResponseDict:
        """
        发送位置分享
        
        :param target_type: 目标类型，"private"或"group"
        :param target_id: 目标ID，用户QQ号或群号
        :param lat: 纬度
        :param lon: 经度
        :param title: 位置标题
        :param content: 位置描述
        :return: API响应结果
        """
        # 创建消息并添加位置
        message_builder = self.create_message()
        if hasattr(message_builder, "location"):
            message_with_location = message_builder.location(lat, lon, title=title, content=content)
            return await self.send_msg(target_type, target_id, message_with_location)
        else:
            logger.error("Message对象没有location方法")
            raise AttributeError("Message对象没有location方法")
    
    async def send_music(self, target_type: Literal["private", "group"], target_id: int, 
                        music_type: Literal["qq", "163", "xm"], music_id: int | str) -> ApiResponseDict:
        """
        发送音乐分享
        
        :param target_type: 目标类型，"private"或"group"
        :param target_id: 目标ID，用户QQ号或群号
        :param music_type: 音乐平台类型，"qq"、"163"或"xm"
        :param music_id: 音乐ID
        :return: API响应结果
        """
        # 创建消息并添加音乐分享
        message_builder = self.create_message()
        if hasattr(message_builder, "music"):
            message_with_music = message_builder.music(music_type, music_id)
            return await self.send_msg(target_type, target_id, message_with_music)
        else:
            logger.error("Message对象没有music方法")
            raise AttributeError("Message对象没有music方法")
    
    async def send_custom_music(self, target_type: Literal["private", "group"], target_id: int, 
                               url: str, audio: str, title: str, content: str | None = None,
                               image: str | None = None) -> ApiResponseDict:
        """
        发送自定义音乐分享
        
        :param target_type: 目标类型，"private"或"group"
        :param target_id: 目标ID，用户QQ号或群号
        :param url: 点击后跳转的链接
        :param audio: 音频文件URL
        :param title: 音乐标题
        :param content: 音乐描述
        :param image: 封面图片URL
        :return: API响应结果
        """
        # 创建消息并添加自定义音乐
        message_builder = self.create_message()
        if hasattr(message_builder, "music_custom"):
            message_with_custom_music = message_builder.music_custom(url, audio, title, content=content, image=image)
            return await self.send_msg(target_type, target_id, message_with_custom_music)
        else:
            logger.error("Message对象没有music_custom方法")
            raise AttributeError("Message对象没有music_custom方法")
    
    async def send_face(self, target_type: Literal["private", "group"], target_id: int, face_id: int) -> ApiResponseDict:
        """
        发送QQ表情
        
        :param target_type: 目标类型，"private"或"group"
        :param target_id: 目标ID，用户QQ号或群号
        :param face_id: 表情ID
        :return: API响应结果
        """
        # 创建消息并添加表情
        message_builder = self.create_message()
        if hasattr(message_builder, "face"):
            message_with_face = message_builder.face(face_id)
            return await self.send_msg(target_type, target_id, message_with_face)
        else:
            logger.error("Message对象没有face方法")
            raise AttributeError("Message对象没有face方法")
    
    async def send_poke(self, target_type: Literal["private", "group"], target_id: int, 
                       user_id: int) -> ApiResponseDict:
        """
        发送戳一戳
        
        :param target_type: 目标类型，"private"或"group"
        :param target_id: 目标ID，用户QQ号或群号
        :param user_id: 要戳的用户QQ号
        :return: API响应结果
        """
        if target_type == "private":
            return await self._call_action(action=ActionType.FRIEND_POKE, params={
                "user_id": user_id
            })
        else:  # group
            return await self._call_action(action=ActionType.GROUP_POKE, params={
                "group_id": target_id,
                "user_id": user_id
            })
    
    async def recall_message(self, message_id: int | str) -> ApiResponseDict:
        """
        撤回消息
        
        :param message_id: 消息ID
        :return: API响应结果
        """
        return await self._call_action(action=ActionType.DELETE_MSG, params={
            "message_id": message_id
        })
    
    async def get_message(self, message_id: int | str) -> ApiResponseDict:
        """
        获取消息
        
        :param message_id: 消息ID
        :return: API响应结果
        """
        return await self._call_action(action=ActionType.GET_MSG, params={
            "message_id": message_id
        })

    async def set_group_kick(self, group_id: int, user_id: int, reject_add_request: bool = False) -> ApiResponseDict:
        """
        踢出群成员
        
        :param group_id: 群号
        :param user_id: 要踢的用户QQ号
        :param reject_add_request: 是否拒绝此人的加群请求
        :return: API响应结果
        """
        return await self._call_action(action=ActionType.SET_GROUP_KICK, params={
            "group_id": group_id,
            "user_id": user_id,
            "reject_add_request": reject_add_request
        })
    
    async def set_group_ban(self, group_id: int, user_id: int, duration: int = 30 * 60) -> ApiResponseDict:
        """
        设置群成员禁言
        
        :param group_id: 群号
        :param user_id: 要禁言的用户QQ号
        :param duration: 禁言时长，单位秒，0表示解除禁言
        :return: API响应结果
        """
        return await self._call_action(ActionType.SET_GROUP_BAN, {
            "group_id": group_id,
            "user_id": user_id,
            "duration": duration
        })
    
    async def set_group_whole_ban(self, group_id: int, enable: bool = True) -> ApiResponseDict:
        """
        设置全员禁言
        
        :param group_id: 群号
        :param enable: 是否开启，True表示开启，False表示关闭
        :return: API响应结果
        """
        return await self._call_action(ActionType.SET_GROUP_WHOLE_BAN, {
            "group_id": group_id,
            "enable": enable
        })
    
    def create_forward_nodes(self, messages: list[tuple[int, str, str | list[MessageSegmentDict]]]) -> list[MessageSegmentDict]:
        """
        创建合并转发消息节点列表
        
        :param messages: 消息列表，每个元素为 (QQ号, 昵称, 消息内容) 的元组
        :return: 节点列表
        """
        nodes: list[MessageSegmentDict] = []
        for user_id, nickname, content in messages:
            # 处理消息内容
            content_segments: list[MessageSegmentDict] = safe_cast_message_segments(
                content if isinstance(content, (str, Message, list)) else str(content)
            )
            
            # 创建节点数据结构 - 不依赖MessageSegment.node_custom
            node_data: MessageSegmentDict = {
                "type": "node",
                "data": {
                    "user_id": user_id,
                    "nickname": nickname,
                    "content": content_segments
                }
            }
            nodes.append(node_data)
            
        return nodes
    
    async def send_forward_msg(self, target_type: Literal["private", "group"], target_id: int, 
                             messages: list[MessageSegmentDict]) -> ApiResponseDict:
        """
        发送合并转发消息
        
        :param target_type: 目标类型，"private"或"group"
        :param target_id: 目标ID，用户QQ号或群号
        :param messages: 节点消息列表
        :return: API响应结果
        """
        if target_type == "private":
            return await self._call_action(ActionType.SEND_PRIVATE_FORWARD_MSG, {
                "user_id": target_id,
                "messages": messages
            })
        else:  # group
            return await self._call_action(ActionType.SEND_GROUP_FORWARD_MSG, {
                "group_id": target_id,
                "messages": messages
            })
    
    def parse_message(self, message: str | list[MessageSegmentDict]) -> Message:
        """
        将API返回的消息数据解析为Message对象
        
        :param message: 消息内容，可以是CQ字符串或消息段列表
        :return: Message对象
        """
        if isinstance(message, str):
            # 尝试解析CQ码字符串
            return cast(Message, Message.from_cq_str(message))
        else:
            # 直接从段列表创建
            return cast(Message, Message.from_segments(message))
    
    def get_message_text(self, message: str | list[MessageSegmentDict] | Message) -> str:
        """
        提取消息中的纯文本内容
        
        :param message: 消息内容
        :return: 纯文本内容
        """
        # 将不同类型的消息转换为Message对象
        if isinstance(message, str):
            message_object = self.parse_message(message)
        elif isinstance(message, list):
            message_object = self.parse_message(message)
        else:
            message_object = message
            
        # 安全地提取纯文本内容
        if hasattr(message_object, "extract_plain_text"):
            return message_object.extract_plain_text()
        else:
            # 如果Message对象没有extract_plain_text方法，尝试手动提取
            logger.warning("Message对象没有extract_plain_text方法，尝试手动提取")
            text_parts: list[str] = []
            
            # 尝试安全地获取消息段
            message_segments: list[MessageSegmentDict] = []
            if hasattr(message_object, "get_segments"):
                message_segments = message_object.get_segments()
            elif isinstance(message_object, list):
                message_segments = message_object
            else:
                logger.warning("无法从Message对象获取消息段")
                return ""
                
            # 从消息段中提取文本内容
            for segment in message_segments:
                if isinstance(segment, dict) and segment.get("type") == "text":
                    data = safe_get_from_dict(segment, "data")
                    text = safe_get_from_dict(data, "text")
                    if isinstance(text, str):
                        text_parts.append(text)
            
            return "".join(text_parts)
    
    def get_message_images(self, message: str | list[MessageSegmentDict] | Message) -> list[str]:
        """
        提取消息中的所有图片URL
        
        :param message: 消息内容
        :return: 图片URL列表
        """
        # 将不同类型的消息统一转换为消息段列表
        message_segments: list[MessageSegmentDict] = []
        if isinstance(message, str):
            message_object = self.parse_message(message)
            if hasattr(message_object, "get_segments"):
                message_segments = message_object.get_segments()
        elif isinstance(message, list):
            message_segments = message
        elif hasattr(message, "get_segments"):
            message_segments = message.get_segments()
        else:
            logger.warning(f"无法从类型 {type(message)} 获取消息段")
            return []
            
        # 从消息段中提取图片URL
        images: list[str] = []
        for segment in message_segments:
            if isinstance(segment, dict) and segment.get("type") == MessageSegmentType.IMAGE:
                # 安全地获取data字段
                data = safe_get_from_dict(segment, "data")
                if isinstance(data, dict):
                    # 优先尝试获取url，如果没有则尝试获取file
                    url = safe_get_from_dict(data, "url")
                    file = safe_get_from_dict(data, "file")
                    img_src = url if url else file
                    if isinstance(img_src, str):
                        images.append(img_src)
        return images
    
    def get_at_targets(self, message: str | list[MessageSegmentDict] | Message) -> list[int]:
        """
        提取消息中@的所有目标QQ号
        
        :param message: 消息内容
        :return: 被@的QQ号列表
        """
        # 将不同类型的消息统一转换为消息段列表
        message_segments: list[MessageSegmentDict] = []
        if isinstance(message, str):
            message_object = self.parse_message(message)
            if hasattr(message_object, "get_segments"):
                message_segments = message_object.get_segments()
        elif isinstance(message, list):
            message_segments = message
        elif hasattr(message, "get_segments"):
            message_segments = message.get_segments()
        else:
            logger.warning(f"无法从类型 {type(message)} 获取消息段")
            return []
            
        # 从消息段中提取@的目标QQ号
        targets: list[int] = []
        for segment in message_segments:
            if isinstance(segment, dict) and segment.get("type") == MessageSegmentType.AT:
                # 安全地获取data字段
                data = safe_get_from_dict(segment, "data")
                if isinstance(data, dict):
                    # 获取qq字段
                    qq = safe_get_from_dict(data, "qq")
                    # 检查是否是有效的QQ号（不是"all"且可转为整数）
                    if isinstance(qq, (str, int)) and str(qq) != "all":
                        try:
                            targets.append(int(qq))
                        except (ValueError, TypeError):
                            logger.warning(f"无法将QQ号转换为整数: {qq}")
                            
        return targets
        
    def has_at_all(self, message: str | list[MessageSegmentDict] | Message) -> bool:
        """
        检查消息是否@全体成员
        
        :param message: 消息内容
        :return: 是否@全体成员
        """
        # 将不同类型的消息统一转换为消息段列表
        message_segments: list[MessageSegmentDict] = []
        if isinstance(message, str):
            message_object = self.parse_message(message)
            if hasattr(message_object, "get_segments"):
                message_segments = message_object.get_segments()
        elif isinstance(message, list):
            message_segments = message
        elif hasattr(message, "get_segments"):
            message_segments = message.get_segments()
        else:
            logger.warning(f"无法从类型 {type(message)} 获取消息段")
            return False
            
        # 检查是否有@全体成员的消息段
        for segment in message_segments:
            if isinstance(segment, dict) and segment.get("type") == MessageSegmentType.AT:
                # 安全地获取data字段
                data = safe_get_from_dict(segment, "data")
                if isinstance(data, dict):
                    # 获取qq字段
                    qq = safe_get_from_dict(data, "qq")
                    if qq == "all":
                        return True
                        
        return False
    
    async def is_at_me(self, event: EventDict) -> bool:
        """
        检查消息是否@了机器人自己
        
        :param event: 事件数据
        :return: 是否@了机器人自己
        """
        # 尝试从事件中获取self_id
        self_id_obj = event.get("self_id") 
        self_id: int | None = None
        if isinstance(self_id_obj, (int, str)) and str(self_id_obj).isdigit():
             self_id = int(self_id_obj)
        
        # 如果事件中没有self_id，尝试从API获取
        if self_id is None:
            self_id = await self.get_self_id()
            
        # 如果仍然无法获取，使用默认值
        if self_id is None and hasattr(self, "_default_self_id"):
            self_id = self._default_self_id
            
        # 如果没有可用的self_id，返回False
        if self_id is None:
            logger.warning("无法确定机器人QQ号，无法判断是否@了机器人")
            return False
            
        # 获取消息内容
        message_obj = event.get("message", [])
        
        # 统一将各种形式的消息转换为可处理的格式 
        if isinstance(message_obj, str):
            message = message_obj
        elif isinstance(message_obj, list) and all(isinstance(item, dict) for item in message_obj): 
            message = message_obj  # 已经是list[MessageSegmentDict]
        elif hasattr(message_obj, "get_segments"):
            # 如果是Message对象，获取其消息段
            message = message_obj.get_segments()
        else:
            logger.warning(f"无法解析消息类型: {type(message_obj)}")
            return False

        # 获取@的目标QQ号
        targets = self.get_at_targets(message)
        
        # 判断机器人自身是否在被@的目标中
        return self_id in targets

    async def get_login_info(self) -> ApiResponseDict:
        """
        获取登录号信息
        
        :return: API响应结果，包含user_id(QQ号)和nickname(昵称)
        """
        return await self._call_action(ActionType.GET_LOGIN_INFO)
    
    async def get_self_id(self) -> int | None:
        """
        获取机器人自己的QQ号
        
        :return: 机器人QQ号，如果获取失败则返回None
        """
        try:
            login_info = await self.get_login_info()
            # Safely access nested dictionary
            data_dict = login_info.get("data")
            if isinstance(data_dict, dict):
                # Check type after .get()
                user_id_obj = data_dict.get("user_id")
                if isinstance(user_id_obj, (str, int)):
                    try:
                        return int(user_id_obj)
                        return int(user_id_obj)
                    except (ValueError, TypeError):
                        logger.warning(f"无法将QQ号转换为整数: {user_id_obj}")
                        return None
            return None
        except Exception as e:
            logger.error(f"获取机器人QQ号失败: {e}")
            return None
            
    def set_default_self_id(self, user_id: int) -> None:
        """
        设置默认的机器人QQ号，在无法从API获取时使用
        
        :param user_id: 默认的机器人QQ号
        """
        self._default_self_id = user_id
        logger.info(f"已设置默认QQ号: {user_id}")

    # 处理get_segments方法的安全调用
    def _safe_get_segments(self, msg_obj: Any) -> MessageSegmentList:
        """安全地获取消息段列表，处理可能不存在的get_segments方法"""
        if hasattr(msg_obj, "get_segments") and callable(getattr(msg_obj, "get_segments")):
            try:
                segments = msg_obj.get_segments()
                # 确保返回类型正确
                return [dict(segment) for segment in segments] if segments else []
            except Exception as e:
                logger.warning(f"调用get_segments方法失败: {e}")
                return []
        elif isinstance(msg_obj, list):
            # 已经是列表形式
            return [dict(segment) for segment in msg_obj if isinstance(segment, dict)]
        elif isinstance(msg_obj, dict):
            # 单个消息段
            return [dict(msg_obj)]
        elif isinstance(msg_obj, str):
            # 纯文本消息
            return [{"type": "text", "data": {"text": msg_obj}}]
        else:
            # 其他类型，尝试转为字符串
            return [{"type": "text", "data": {"text": str(msg_obj)}}]

