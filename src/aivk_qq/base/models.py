from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
from .enums import ActionType

# 发送者信息模型
class Sender(BaseModel):
    user_id: int
    nickname: str
    card: str = ""


# 消息段数据模型
class MessageSegmentData(BaseModel):
    text: Optional[str] = None
    # 可以根据需要添加其他字段，如图片URL、文件信息等


# 消息段模型
class MessageSegment(BaseModel):
    type: str
    data: MessageSegmentData


# 生命周期事件模型
class LifecycleEvent(BaseModel):
    time: int
    self_id: int
    post_type: str = "meta_event"
    meta_event_type: str = "lifecycle"
    sub_type: str = "connect"


# 私聊消息模型
class PrivateMessage(BaseModel):
    self_id: int
    user_id: int
    time: int
    message_id: int
    message_seq: int
    real_id: int
    real_seq: str
    message_type: str = "private"
    sender: Sender
    raw_message: str
    font: int
    sub_type: str = "friend"
    message: List[MessageSegment]
    message_format: str = "array"
    post_type: str = "message"
    target_id: int


# 通用消息模型，可以是生命周期事件或私聊消息
class Message(BaseModel):
    """通用消息模型，可以处理不同类型的消息"""
    
    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> Union[LifecycleEvent, PrivateMessage, Any]:
        """
        从JSON数据创建相应的消息模型
        
        :param json_data: 解析后的JSON数据字典
        :return: 相应类型的消息模型实例
        """
        if not isinstance(json_data, dict):
            raise ValueError("JSON数据必须是字典类型")
            
        # 根据post_type和其他字段判断消息类型
        post_type = json_data.get("post_type")
        
        if post_type == "meta_event" and json_data.get("meta_event_type") == "lifecycle":
            return LifecycleEvent(**json_data)
        elif post_type == "message" and json_data.get("message_type") == "private":
            return PrivateMessage(**json_data)
        else:
            # 对于其他类型的消息，可以根据需要扩展
            return json_data

# 示例使用:
# import json
# 
# # 解析生命周期事件
# lifecycle_json = '{"time":1744662067,"self_id":123456,"post_type":"meta_event","meta_event_type":"lifecycle","sub_type":"connect"}'
# lifecycle_data = json.loads(lifecycle_json)
# lifecycle_event = Message.from_json(lifecycle_data)
# 
# # 解析私聊消息
# private_msg_json = '{"self_id":123456,"user_id":234567,"time":1744662076,"message_id":364805473,"message_seq":364805473,"real_id":364805473,"real_seq":"382","message_type":"private","sender":{"user_id":2418701971,"nickname":"用户名","card":""},"raw_message":"你好","font":14,"sub_type":"friend","message":[{"type":"text","data":{"text":"你好"}}],"message_format":"array","post_type":"message","target_id":123456}'
# private_msg_data = json.loads(private_msg_json)
# private_message = Message.from_json(private_msg_data)

# region 发送 & 接收数据包类

class WsPayload(BaseModel):
    action : ActionType
    params : dict
    echo : str


class WsResponse(BaseModel):
    status : str
    retcode : int
    data : dict
    echo : str


class HttpPayload(BaseModel):
    """OneBot HTTP API 请求参数基类"""
    # 通用字段可以在这里定义
    
    class Config:
        extra = "allow"  # 允许额外字段，这样不同API的特定参数可以正常传入

class HttpResponse(BaseModel):
    status : str
    retcode : int
    msg : Optional[str]
    wording : Optional[str]
    data : dict
    echo : str

# HTTP-SSE 事件订阅模型
class SseConnection(BaseModel):
    """HTTP-SSE 连接配置"""
    endpoint: str = "/_events"  # SSE 事件订阅端点
    heartbeat_interval: int = 30  # 心跳间隔（秒）
    
    class Config:
        extra = "allow"

# HTTP-SSE 事件数据模型
class SseEvent(BaseModel):
    """HTTP-SSE 事件数据"""
    id: Optional[str] = None  # 事件ID
    event: Optional[str] = None  # 事件类型
    data: Dict[str, Any]  # 事件数据
    retry: Optional[int] = None  # 重连延迟（毫秒）
    
    def format_sse(self) -> str:
        """格式化为 SSE 事件格式"""
        lines = []
        if self.id is not None:
            lines.append(f"id: {self.id}")
        if self.event is not None:
            lines.append(f"event: {self.event}")
        if self.retry is not None:
            lines.append(f"retry: {self.retry}")