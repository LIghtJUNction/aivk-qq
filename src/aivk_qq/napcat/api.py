# -*- coding: utf-8 -*-
from logging import Logger

import enum
from typing import Literal, ClassVar
from collections.abc import AsyncGenerator
from pydantic import BaseModel
from pydantic_core import Url
import logging

from websockets.legacy.server import serve, WebSocketServerProtocol

# 改回相对导入
from .server import NapcatHttpServer
import aiohttp


logger: Logger = logging.getLogger(name=__name__)

# 枚举 -- 端口号和主机地址配置

class NapcatPort(enum.Enum):
    """
    Napcat 端口枚举类
    """
    HTTP_CLIENT = 10143
    HTTP_SSE_CLIENT = 10144
    WS_CLIENT = 10145
    HTTP_SERVER = 10146
    WS_SERVER = 10147
    
    @classmethod
    def update(cls, name: str, port: int) -> None:
        """
        更新指定名称的端口号
        
        :param name: 端口名称
        :param port: 新的端口号
        """
        if hasattr(cls, name):
            setattr(cls, name, port)
            logger.info(f"更新端口: {name} = {port}")
        else:
            logger.warning(f"端口名称 {name} 不存在，无法更新")
            raise ValueError(f"端口名称 {name} 不存在，无法更新")
class NapcatHost(enum.Enum):
    """
    Napcat HOST枚举类
    """
    HTTP_CLIENT = "127.0.0.1"
    HTTP_SSE_CLIENT = "127.0.0.1"
    WS_CLIENT = "127.0.0.1"
    HTTP_SERVER = "127.0.0.1"
    WS_SERVER = "127.0.0.1"

    @classmethod
    def update(cls, name: str, host: str) -> None:
        """
        更新指定名称的主机地址
        
        :param name: 主机名称
        :param host: 新的主机地址
        """
        if hasattr(cls, name):
            setattr(cls, name, host)
            logger.info(f"更新主机: {name} = {host}")
        else:
            logger.warning(f"主机名称 {name} 不存在，无法更新")
            raise ValueError(f"主机名称 {name} 不存在，无法更新")
    

class NapcatType(enum.Enum):    
    """
    Napcat 类型枚举类
    """
    HTTP_CLIENT = "HTTP/CLIENT"
    HTTP_SSE_CLIENT = "HTTP/CLIENT/SSE"
    WS_CLIENT = "WS/CLIENT"
    HTTP_SERVER = "HTTP/SERVER"
    WS_SERVER = "WS/SERVER"


# region NapcatAPI
class NapcatAPI(BaseModel):
    # 添加类型注解
    WS_CLIENT: ClassVar[str] = "WS/CLIENT"
    HTTP_CLIENT: ClassVar[str] = "HTTP/CLIENT"
    """
    提供基本对象
    API 低级封装

    请调用以下类方法创建实例：
    - NapcatAPI.NapcatHttpClient()
    - NapcatAPI.NapcatHttpSSEClient()
    - NapcatAPI.NapcatHttpServer()
    - NapcatAPI.NapCatHttpServer()
    - NapcatAPI.NapcatWebSocketClient()
    - NapcatAPI.NapcatWebSocketServer()

    提示：
        SERVER < - > CLIENT 别配置错了
        使用server实例意味着你要去配置client
        使用client实例意味着你要去配置server

    LLM集成配置说明：
    1. 在NapcatHttpClient配置中设置LLM_ENDPOINT参数指向大模型API地址
    2. 通过TOKEN参数传递大模型访问凭证
    3. 使用msgtype参数指定消息格式：
       - "Array"：适用于多轮对话场景
       - "String"：适用于单轮问答场景
    4. 启用WS=True时支持流式响应
    5. 示例配置：
       NapcatAPI.NapcatHttpClient(
           HOST="llm.api.example.com",
           PORT=443,
           TOKEN="sk-xxxxxxxx",
           MSGTYPE="Array",
           WS=True
       )
    """
    # Pydantic模型字段声明
    name: str                                         # 实例名称，用于在metadata中索引
    host: str                                         # 主机地址，用于服务器绑定或客户端连接
    port: int                                         # 端口号，指定服务运行的端口
    ws_path: str                                      # WebSocket路径，默认为"/aivk/qq"
    token: str | None = None                          # 认证令牌，用于安全验证，可为None
    msgtype: Literal["Array", "String"] = "Array"     # 消息格式，可选值为"Array"或"String"
    cors: bool = True                                 # 是否启用跨域资源共享
    ws: bool = True                                   # 是否启用WebSocket
    type_: NapcatType | None = None                   # 实例类型，会在创建实例时设置
    http_url: Url | None = None                       # HTTP URL
    ws_url: Url | None = None                         # WebSocket URL
    
    # 动态创建的字段，在运行时会被实例化
    http_client: aiohttp.ClientSession | None = None  # HTTP客户端实例
    http_server: NapcatHttpServer | None = None     # HTTP服务器实例
    # Store URL instead of connect function
    ws_client_url: str | None = None                  # WebSocket client connection URL
    ws_server: serve | None = None                    # WebSocket服务器实例
    sse_session: aiohttp.ClientSession | None = None  # SSE会话实例
    sse_response: aiohttp.ClientResponse | None = None# SSE响应实例
    
    # 不应该被包含在模型中的字段，使用类变量
    metadata: ClassVar[dict[str, "NapcatAPI"]] = {}   # 静态属性，保存了所有实例的引用
    
    class Config:
        arbitrary_types_allowed: bool = True          # 允许使用非Pydantic原生支持的类型

    def __init__(
        self, 
        HOST: str, 
        PORT: int, 
        WS_PATH: str, 
        TOKEN: str | None, 
        NAME: str, 
        MSGTYPE: Literal["Array", "String"] = "Array", 
        CORS: bool = True, 
        WS: bool = True,
        **kwargs: object
    ) -> None:
        """
        初始化NapcatAPI对象
        
        :param HOST: 主机地址，用于服务器绑定或客户端连接
        :param PORT: 端口号，指定服务运行的端口
        :param WS_PATH: WebSocket路径，默认为"/aivk/qq"
        :param TOKEN: 认证令牌，用于安全验证，可为None
        :param NAME: 实例名称，用于在metadata中索引
        :param MSGTYPE: 消息格式，可选值为"Array"或"String"，默认为"Array"
        :param CORS: 是否启用跨域资源共享，默认为True
        :param WS: 是否启用WebSocket，默认为True
        """
        # 调用父类初始化方法，将参数传递给Pydantic的BaseModel
        super().__init__(
            name=NAME, 
            host=HOST, 
            port=PORT, 
            ws_path=WS_PATH,
            token=TOKEN,
            msgtype=MSGTYPE,
            cors=CORS,
            ws=WS,
            **kwargs
        )
        

    # region 内部方法
    
    def _TYPE_CHECK(self, type_: NapcatType) -> None:
        """
        检查实例类型是否匹配预期类型
        
        :param type_: 预期的类型，使用NapcatType枚举值
        :raises ValueError: 如果类型不匹配则抛出异常
        """
        if self.type_ != type_:
            raise ValueError(f"类型不匹配: {self.type_.value if self.type_ else None} != {type_.value}")
        





    # region ==========


    












    # region 基本实例方法

    """

    注释 等待补充 TODO
    
    """















    # region SERVER_BINDING
    def HTTP_SERVER_BINDING(self) -> None:
        """
        设置HTTP服务器绑定地址和端口
        
        :raises ValueError: 如果实例类型不是 HTTP_SERVER 则抛出异常
        """
        self._TYPE_CHECK(type_=NapcatType.HTTP_SERVER)
        self.http_server = NapcatHttpServer(HOST=self.host, PORT=self.port, TOKEN=self.token, MSGTYPE=self.msgtype)
        logger.info(msg=f"HTTP Server bound to {self.host}:{self.port}")








    # region WS_SERVER_BINDING
    def WS_SERVER_BINDING(self) -> None:
        """
        设置WebSocket服务器绑定地址和端口
        
        如果设置了TOKEN，将验证客户端连接中的access_token参数
        
        :raises ValueError: 如果实例类型不是 WS_SERVER 则抛出异常
        """
        self._TYPE_CHECK(NapcatType.WS_SERVER)

        from .server import ws_handler
        async def handler_with_token(websocket: WebSocketServerProtocol, path: str):
            await ws_handler(websocket, path, token=self.token)
        # 修正参数顺序，避免关键字参数在位置参数前
        self.ws_server = serve(handler_with_token, self.host, self.port)
        logger.info(msg=f"WebSocket服务器已绑定到 {self.host}:{self.port}")
        if self.token:
            logger.info(msg="WebSocket服务器已启用TOKEN验证")
        else:
            logger.info("WebSocket服务器未使用TOKEN验证")





    # region HCC
    def HTTP_CLIENT_CONNECT(self) -> None:
        """
        设置HTTP客户端连接地址和端口
        
        如果设置了TOKEN，将在客户端会话中添加Bearer认证头
        如果设置了WS=True，同时会设置WebSocket客户端连接
        
        :raises ValueError: 如果实例类型不是 HTTP_CLIENT 则抛出异常
        """
        self._TYPE_CHECK(type_=NapcatType.HTTP_CLIENT)
        
        # 设置默认请求头，包含认证信息
        default_headers: dict[str, str] = {}
        if self.token:
            default_headers['Authorization'] = f'Bearer {self.token}'
            logger.debug(msg=f"已设置HTTP客户端Bearer认证头: Bearer {self.token}")
        
        # 将URL对象转换为字符串，以便用于aiohttp.ClientSession
        base_url_str: str | None = str(self.http_url) if self.http_url else None
        self.http_client = aiohttp.ClientSession(base_url=base_url_str, headers=default_headers)
        logger.info(msg=f"HTTP客户端已连接到 {self.host}:{self.port}")
        
        # 如果启用了WebSocket，也设置WebSocket客户端连接
        if self.ws and self.ws_url:
            # 构建WebSocket URL，如果有TOKEN则添加access_token参数
            ws_url: str | None = str(self.ws_url)
            if self.token:
                # 添加access_token参数进行认证
                ws_url += f"?access_token={self.token}"
                logger.debug(msg=f"WebSocket URL已添加TOKEN参数: {ws_url}")
            
            self.ws_client_url = ws_url
            logger.info(msg=f"HTTP客户端模式下的WebSocket客户端已准备连接到 {self.host}:{self.port}{self.ws_path}")
    




    # region HCSC
    async def HTTP_CLIENT_SSE_CONNECT(self) -> None:
        """
        设置HTTP SSE客户端连接地址和端口，使用aiohttp库实现
        
        这是一个异步方法，需要在异步环境中调用。
        如果设置了TOKEN，会自动添加Bearer认证头。
        如果设置了WS=True，同时会设置WebSocket客户端连接。
        
        :raises ValueError: 如果实例类型不是 HTTP_SSE_CLIENT 则抛出异常
        :raises aiohttp.ClientError: 连接失败时抛出异常
        
        使用示例:
        ```python
        # 在异步函数中调用
        async def connect_and_listen():
            await napcat_client.HTTP_CLIENT_SSE_CONNECT()
            async for event in napcat_client.sse_events():
                print(f"收到事件: {event}")
        
        # 运行异步函数
        asyncio.run(connect_and_listen())
        ```
        """
        self._TYPE_CHECK(NapcatType.HTTP_SSE_CLIENT)
        
        # 准备请求头，包含认证信息
        headers = {
            'Accept': 'text/event-stream',  # SSE必需的头部
            'Cache-Control': 'no-cache'     # 避免缓存
        }
        
        # 添加认证头
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            logger.debug(f"已设置SSE客户端Bearer认证头: Bearer {self.token}")
        

        # 创建会话，将请求头与base_url作为参数传入
        self.sse_session = aiohttp.ClientSession(
            base_url=str(self.http_url),
            headers=headers
        )
        logger.info(f"准备连接到HTTP SSE服务器 {self.host}:{self.port}")
        
        try:
            # 使用已构建的HTTP_URL，而不是重新构建URL
            # 创建请求但不等待响应完成
            self.sse_response = await self.sse_session.get(
                str(self.http_url), 
                timeout=aiohttp.ClientTimeout(total=None)  # 禁用超时，允许长连接
            )
            
            # 检查响应状态
            if self.sse_response.status != 200:
                error_text = await self.sse_response.text()
                await self.sse_session.close()
                
                # 特殊处理认证错误
                if self.sse_response.status == 401:
                    logger.error("SSE连接失败: TOKEN认证失败")
                    raise aiohttp.ClientError("TOKEN认证失败")
                
                raise aiohttp.ClientError(f"SSE连接失败，状态码: {self.sse_response.status}, 响应: {error_text}")
            
            logger.info(f"HTTP SSE客户端已成功连接到 {self.host}:{self.port}")
            if self.token:
                logger.debug("TOKEN验证已通过")
            
            # 如果启用了WebSocket，也设置WebSocket客户端连接
            if self.ws and self.ws_url:
                # 构建WebSocket URL，如果有TOKEN则添加access_token参数
                ws_url = str(self.ws_url)
                if self.token:
                    # 添加access_token参数进行认证
                    ws_url += f"?access_token={self.token}"
                    logger.debug(f"WebSocket URL已添加TOKEN参数: {ws_url}")
                
                self.ws_client_url = ws_url
                logger.info(f"HTTP SSE客户端模式下的WebSocket客户端已准备连接到 {self.host}:{self.port}{self.ws_path}")
                
                
        except Exception as e:
            # 确保在异常情况下关闭会话
            if hasattr(self, 'sse_session'):
                await self.sse_session.close()
            logger.error(f"SSE连接失败: {str(e)}")
            raise
    



    # region sse_events
    async def sse_events(self) -> AsyncGenerator[dict[str, str | None], None]:
        """
        返回一个异步迭代器，用于获取SSE事件流
        
        :yields: 解析后的SSE事件字典，包含event和data字段
        :raises: RuntimeError 如果在调用HTTP_CLIENT_SSE_CONNECT之前调用
        
        使用示例:
        ```python
        await client.HTTP_CLIENT_SSE_CONNECT()
        async for event in client.sse_events():
            print(f"事件类型: {event['event']}")
            print(f"事件数据: {event['data']}")
        ```
        """
        if not hasattr(self, 'sse_response') or self.sse_response is None:
            raise RuntimeError("请先调用HTTP_CLIENT_SSE_CONNECT方法建立SSE连接")
        
        try:
            # SSE事件解析状态
            event_type: str | None = None
            data_buffer: list[str] = []
            
            # 按行读取响应内容
            async for line_bytes in self.sse_response.content:
                line: str = line_bytes.decode(encoding='utf-8').rstrip()
                
                # 空行表示事件结束
                if not line:
                    if data_buffer:
                        data = '\n'.join(data_buffer)
                        yield {
                            'event': event_type or 'message',
                            'data': data
                        }
                        # 重置缓冲区
                        event_type = None
                        data_buffer = []
                    continue
                    
                # 处理事件行
                if line.startswith('event:'):
                    event_type = line[6:].strip()
                elif line.startswith('data:'):
                    data_buffer.append(line[5:].strip())
                # 忽略其他行类型如id:和retry:
                
        except Exception as e:
            logger.error(f"处理SSE事件流时出错: {str(e)}")
            raise
        finally:
            # 确保关闭会话
            if hasattr(self, 'sse_session') and self.sse_session:
                await self.sse_session.close()
                logger.info("SSE会话已关闭")




    # region WS_CLIENT_CONNECT
    def WS_CLIENT_CONNECT(self) -> None:
        """
        设置WebSocket客户端连接地址和端口
        
        如果设置了TOKEN，将通过URL参数access_token进行验证
        
        :raises ValueError: 如果实例类型不是 WS_CLIENT 则抛出异常
        """
        self._TYPE_CHECK(NapcatType.WS_CLIENT)
        
        # 构建WebSocket URL，如果有TOKEN则添加access_token参数
        ws_url = str(self.ws_url)
        if self.token:
            # 添加access_token参数进行认证
            ws_url += f"?access_token={self.token}"
            logger.debug(f"WebSocket URL已添加TOKEN参数: {ws_url}")
        
        self.ws_client_url = ws_url
        logger.info(f"WebSocket Client connected to {self.host}:{self.port}")
        if self.token:
            logger.debug("已通过URL参数方式设置WebSocket认证")
    





    # region =======










    # region 获取实例







    














    # region HTTP CLIENT

    @classmethod
    def NapcatHttpClient(
        cls,
        HOST: str = NapcatHost.HTTP_CLIENT.value, 
        PORT: int = NapcatPort.HTTP_CLIENT.value, 
        WS_PATH: str = "/aivk/qq", 
        TOKEN: str | None = None,
        NAME: str = "NapcatHttpClient", 
        MSGTYPE: Literal["Array", "String"] = "Array", 
        CORS: bool = True, 
        WS: bool = True
    ) -> "NapcatAPI":
        """
        创建HTTP客户端API实例
        
        请在Napcat配置：
        HTTP服务器 -- 启用CORS -- 可选启用WS
        
        :param HOST: 主机地址，用于连接到服务器，默认为"127.0.0.1"
        :param PORT: 端口号，默认为10143
        :param WS_PATH: WebSocket路径，默认为"/aivk/qq"
        :param TOKEN: 认证令牌，可选
        :param NAME: 实例名称，用于在metadata中索引
        :param MSGTYPE: 消息格式，可选值为"Array"或"String"，默认为"Array"
        :param CORS: 是否启用跨域资源共享，默认为True
        :param WS: 是否启用WebSocket，默认为True
        :return: NapcatAPI对象
        
        示例配置:
        主机: 127.0.0.1
        端口: 10144
        消息格式: Array
        TOKEN: None
        CORS: 已启用
        WS: 已启用
        """
        _NapcatHttpClient = cls(HOST=HOST, PORT=PORT, WS_PATH=WS_PATH, TOKEN=TOKEN, NAME=NAME, MSGTYPE=MSGTYPE, CORS=CORS, WS=WS)
        _NapcatHttpClient.http_url = Url.build(scheme="http", host=HOST, port=PORT, path="/")
        _NapcatHttpClient.ws_url = Url.build(scheme="ws", host=HOST, port=PORT, path=WS_PATH) if WS else None

        logger.debug(_NapcatHttpClient)
        NapcatAPI.metadata[NAME] = _NapcatHttpClient
        NapcatAPI.metadata[NAME].type_ = NapcatType.HTTP_CLIENT
        return _NapcatHttpClient




    # region SSE CLIENT

    @classmethod
    def NapcatHttpSSEClient(
        cls,
        HOST: str = NapcatHost.HTTP_SSE_CLIENT.value, 
        PORT: int = NapcatPort.HTTP_SSE_CLIENT.value, 
        WS_PATH: str = "/aivk/qq", 
        TOKEN: str | None = None,
        NAME: str = "NapcatHttpSSEClient", 
        MSGTYPE: Literal["Array", "String"] = "Array", 
        CORS: bool = True, 
        WS: bool = True
    ) -> "NapcatAPI":
        """
        创建HTTP SSE客户端API实例
        
        请在Napcat配置：
        HTTP SSE服务器 -- 启用CORS -- 可选启用WS
        
        :param HOST: 主机地址，用于连接到服务器，默认为"127.0.0.1"
        :param PORT: 端口号，默认为10144
        :param WS_PATH: WebSocket路径，默认为"/aivk/qq"
        :param TOKEN: 认证令牌，用于安全验证，可选
        :param NAME: 实例名称，用于在metadata中索引
        :param MSGTYPE: 消息格式，可选值为"Array"或"String"，默认为"Array"
        :param CORS: 是否启用跨域资源共享，默认为True
        :param WS: 是否启用WebSocket，默认为True
        :return: NapcatAPI对象
        
        示例配置:
        主机: 127.0.0.1
        端口: 10144
        消息格式: Array
        TOKEN: None
        CORS: 已启用
        WS: 已启用
        """
        _NapcatHttpClient = cls(HOST=HOST, PORT=PORT, WS_PATH=WS_PATH, TOKEN=TOKEN, NAME=NAME, MSGTYPE=MSGTYPE, CORS=CORS, WS=WS)
        _NapcatHttpClient.http_url = Url.build(scheme="http", host=HOST, port=PORT, path="/")
        _NapcatHttpClient.ws_url = Url.build(scheme="ws", host=HOST, port=PORT, path=WS_PATH) if WS else None

        logger.debug(_NapcatHttpClient)
        NapcatAPI.metadata[NAME] = _NapcatHttpClient
        NapcatAPI.metadata[NAME].type_ = NapcatType.HTTP_SSE_CLIENT
        return _NapcatHttpClient




    # region WS CLIENT
    @classmethod
    def NapcatWebSocketClient(
        cls, 
        HOST: str = NapcatHost.WS_CLIENT.value, 
        PORT: int = NapcatPort.WS_CLIENT.value, 
        WS_PATH: str = "/aivk/qq", 
        TOKEN: str | None = None, 
        NAME: str = "NapcatWebSocketClient", 
        MSGTYPE: Literal["Array", "String"] = "Array"
    ) -> "NapcatAPI":
        """
        创建WebSocket客户端API实例
        
        请在Napcat配置：
        WebSocket服务器
        
        :param HOST: 主机地址，用于连接到WebSocket服务器，默认为"127.0.0.1"
        :param PORT: 端口号，默认为10145
        :param WS_PATH: WebSocket路径，默认为"/aivk/qq"
        :param TOKEN: 认证令牌，用于安全验证，可选
        :param NAME: 实例名称，用于在metadata中索引
        :param MSGTYPE: 消息格式，可选值为"Array"或"String"，默认为"Array"
        :return: NapcatAPI对象
        """
        _NapcatWebSocketClient = cls(NAME=NAME, HOST=HOST, PORT=PORT, TOKEN=TOKEN, WS_PATH=WS_PATH, MSGTYPE=MSGTYPE)
        NapcatAPI.metadata[NAME] = _NapcatWebSocketClient  
        NapcatAPI.metadata[NAME].http_url = None
        NapcatAPI.metadata[NAME].ws_url = Url.build(scheme="ws", host=HOST, port=PORT, path=WS_PATH) 
        NapcatAPI.metadata[NAME].type_ = NapcatType.WS_CLIENT
        return _NapcatWebSocketClient
    



    # region HTTP SERVER

    @classmethod
    def NapcatHttpServer(
        cls, 
        HOST: str = NapcatHost.HTTP_SERVER.value, 
        PORT: int = NapcatPort.HTTP_SERVER.value, 
        TOKEN: str | None = None, 
        NAME: str = "NapcatHttpServer", 
        MSG_TYPE: Literal["Array", "String"] = "Array"
    ) -> "NapcatAPI":
        """
        请在Napcat 配置：
        HTTP 客户端
        http://127.0.0.1:10144
        
        :param HOST: 主机地址，默认为"127.0.0.1"
        :param PORT: 端口号，默认为10146
        :param TOKEN: 认证令牌 (可选)
        :param NAME: 实例名称
        :param MSG_TYPE: 消息格式，默认为"Array"
        :return: NapcatAPI对象

        """
        _NapcatHttpServer = cls(NAME=NAME, HOST=HOST, PORT=PORT, TOKEN=TOKEN, WS_PATH="/aivk/qq", MSGTYPE=MSG_TYPE)
        _NapcatHttpServer.HTTP_SERVER_BINDING() # 调用修正后的方法名
        NapcatAPI.metadata[NAME] = _NapcatHttpServer
        NapcatAPI.metadata[NAME].type_ = NapcatType.HTTP_SERVER
        return _NapcatHttpServer


    # region WS SERVER
    @classmethod
    def NapcatWebSocketServer(
        cls,
        HOST: str = NapcatHost.WS_SERVER.value, 
        PORT: int = NapcatPort.WS_SERVER.value, 
        WS_PATH: str = "/aivk/qq", 
        TOKEN: str | None = None, 
        NAME: str = "NapcatWebSocketServer", 
        MSGTYPE: Literal["Array", "String"] = "Array"
    ) -> "NapcatAPI":
        """
        创建WebSocket服务器API实例
        
        请在Napcat配置：
        WebSocket客户端
        
        :param HOST: 主机地址，用于绑定WebSocket服务器，默认为"127.0.0.1"
        :param PORT: 端口号，默认为10147
        :param WS_PATH: WebSocket路径，默认为"/aivk/qq"
        :param TOKEN: 认证令牌，用于安全验证，可选
        :param NAME: 实例名称，用于在metadata中索引
        :param MSGTYPE: 消息格式，可选值为"Array"或"String"，默认为"Array"
        :return: NapcatAPI对象
        """
        _NapcatWebSocketServer = cls(HOST=HOST, PORT=PORT, WS_PATH=WS_PATH, TOKEN=TOKEN, NAME=NAME, MSGTYPE=MSGTYPE)
        NapcatAPI.metadata[NAME] = _NapcatWebSocketServer  
        NapcatAPI.metadata[NAME].http_url = None
        NapcatAPI.metadata[NAME].ws_url = Url.build(scheme="ws", host=HOST, port=PORT, path=WS_PATH) 
        NapcatAPI.metadata[NAME].type_ = NapcatType.WS_SERVER
        return _NapcatWebSocketServer


    # region =======


    # region END
