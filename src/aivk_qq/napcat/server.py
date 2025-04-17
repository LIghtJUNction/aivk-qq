from logging import Logger
from typing import Literal
from pydantic import BaseModel
import logging
from websockets.legacy.server import WebSocketServerProtocol  # type: ignore
import urllib.parse

logger: Logger = logging.getLogger(name=__name__)

# region Napcat HTTP Server
class NapcatHttpServer(BaseModel):
    """
    Napcat HTTP Server

    > ..api.NapcatAPI : TODO

    进阶 : Napcat将作为client 连接到本server

    """
    HOST: str
    PORT: int
    TOKEN: str | None
    MSGTYPE: Literal["Array", "String"]
    
    def __init__(self, HOST: str, PORT: int, TOKEN: str | None = None, MSGTYPE: Literal["Array", "String"] = "Array") -> None:
        """
        初始化Napcat HTTP服务器
        
        :param HOST: 服务器监听的主机地址
        :param PORT: 服务器监听的端口号
        :param TOKEN: 可选的身份验证令牌
        :param MSGTYPE: 消息类型，可选"Array"或"String"
        """
        super().__init__(HOST=HOST, PORT=PORT, TOKEN=TOKEN, MSGTYPE=MSGTYPE)





# region WebSocket连接处理程序

 # 定义WebSocket连接处理程序，添加TOKEN验证
async def ws_handler(websocket: WebSocketServerProtocol, path: str, token: str | None = None) -> None:
    """
    WebSocket连接处理程序，支持TOKEN验证
    
    :param websocket: WebSocket连接对象
    :param path: 请求路径，可能包含查询参数
    :param token: 可选的身份验证令牌，如果提供将验证客户端TOKEN
    :raises: 可能抛出WebSocket连接相关的异常
    
    功能说明:
    1. 如果提供了token参数，会验证客户端连接中的access_token参数
    2. 验证通过后处理WebSocket消息循环
    3. 默认简单回显接收到的消息
    """

    # 验证TOKEN（如果已设置）
    if token:
        try:
            # 解析查询参数
            if "?" in path:
                # 按第一个问号拆分获取查询字符串
                query_string: str = path.split(sep="?", maxsplit=1)[1]
                params: dict[str, str] = dict(urllib.parse.parse_qsl(qs=query_string))
                
                if "access_token" not in params or params["access_token"] != token:
                    logger.warning(msg=f"WebSocket连接验证失败: TOKEN不匹配，来自 {websocket.remote_address}") 
                    await websocket.close(code=1008, reason="认证失败")  # 1008是策略违规的关闭代码
                    return
                
                logger.info(msg=f"WebSocket连接TOKEN验证成功，来自 {websocket.remote_address}")
            else:
                logger.warning(msg=f"WebSocket连接验证失败: 未提供TOKEN，来自 {websocket.remote_address}")
                await websocket.close(code=1008, reason="认证失败")
                return
        except Exception as e:
            logger.error(msg=f"WebSocket连接验证时出错: {e}")
            await websocket.close(code=1011, reason="服务器内部错误")  # 1011是服务器内部错误的关闭代码
            return
    
    # 连接已认证，处理WebSocket消息
    try:
        async for message in websocket:
            # 处理接收到的消息
            # 这里可以添加消息处理逻辑
            # 例如解析JSON、触发事件等
            logger.debug(f"收到WebSocket消息: {message}")
            
            # 示例：简单地将消息回显给客户端
            await websocket.send(f"收到消息: {message}")
            
    except Exception as e:
        logger.error(f"处理WebSocket消息时出错: {e}")
