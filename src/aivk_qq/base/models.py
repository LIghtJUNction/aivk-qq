from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel


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

