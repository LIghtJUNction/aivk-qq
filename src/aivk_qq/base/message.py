from typing import Dict, List, Union, Optional, Any
import json
import base64
from pathlib import Path
import os

from ..base.enums import MessageSegmentType


class MessageSegment:
    """消息段"""
    
    @staticmethod
    def text(text: str) -> Dict[str, Any]:
        """
        纯文本消息段
        
        :param text: 文本内容
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.TEXT,
            "data": {
                "text": text
            }
        }
    
    @staticmethod
    def face(id: int) -> Dict[str, Any]:
        """
        QQ表情
        
        :param id: 表情ID
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.FACE,
            "data": {
                "id": str(id)
            }
        }
    
    @staticmethod
    def image(file: Union[str, Path, bytes], 
              type: Optional[str] = None, 
              url: Optional[str] = None, 
              cache: bool = True, 
              proxy: bool = True, 
              timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        图片消息段
        
        :param file: 图片文件名、路径、URL或图片bytes数据
        :param type: 图片类型，可选 "flash"表示闪照
        :param url: 图片URL
        :param cache: 是否使用已缓存的文件
        :param proxy: 是否通过代理下载文件
        :param timeout: 下载超时时间，单位秒
        :return: 消息段字典
        """
        data = {"cache": cache, "proxy": proxy}
        
        if isinstance(file, bytes):
            data["file"] = f"base64://{base64.b64encode(file).decode()}"
        elif isinstance(file, (str, Path)) and os.path.exists(str(file)):
            with open(str(file), "rb") as f:
                data["file"] = f"base64://{base64.b64encode(f.read()).decode()}"
        else:
            data["file"] = str(file)
        
        if type:
            data["type"] = type
        if url:
            data["url"] = url
        if timeout:
            data["timeout"] = timeout
            
        return {
            "type": MessageSegmentType.IMAGE,
            "data": data
        }
    
    @staticmethod
    def record(file: Union[str, Path, bytes], 
               magic: bool = False, 
               cache: bool = True, 
               proxy: bool = True, 
               timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        语音消息段
        
        :param file: 语音文件名、路径、URL或语音bytes数据
        :param magic: 是否为变声语音
        :param cache: 是否使用已缓存的文件
        :param proxy: 是否通过代理下载文件
        :param timeout: 下载超时时间，单位秒
        :return: 消息段字典
        """
        data = {"cache": cache, "proxy": proxy, "magic": magic}
        
        if isinstance(file, bytes):
            data["file"] = f"base64://{base64.b64encode(file).decode()}"
        elif isinstance(file, (str, Path)) and os.path.exists(str(file)):
            with open(str(file), "rb") as f:
                data["file"] = f"base64://{base64.b64encode(f.read()).decode()}"
        else:
            data["file"] = str(file)
            
        if timeout:
            data["timeout"] = timeout
            
        return {
            "type": MessageSegmentType.RECORD,
            "data": data
        }
    
    @staticmethod
    def video(file: Union[str, Path, bytes], 
              cache: bool = True, 
              proxy: bool = True, 
              timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        视频消息段
        
        :param file: 视频文件名、路径、URL或视频bytes数据
        :param cache: 是否使用已缓存的文件
        :param proxy: 是否通过代理下载文件
        :param timeout: 下载超时时间，单位秒
        :return: 消息段字典
        """
        data = {"cache": cache, "proxy": proxy}
        
        if isinstance(file, bytes):
            data["file"] = f"base64://{base64.b64encode(file).decode()}"
        elif isinstance(file, (str, Path)) and os.path.exists(str(file)):
            with open(str(file), "rb") as f:
                data["file"] = f"base64://{base64.b64encode(f.read()).decode()}"
        else:
            data["file"] = str(file)
            
        if timeout:
            data["timeout"] = timeout
            
        return {
            "type": MessageSegmentType.VIDEO,
            "data": data
        }
    
    @staticmethod
    def at(qq: Union[int, str], name: Optional[str] = None) -> Dict[str, Any]:
        """
        @某人消息段
        
        :param qq: 被@的QQ号，all表示@全体成员
        :param name: 自定义@的昵称，当qq为all时无效
        :return: 消息段字典
        """
        data = {"qq": str(qq)}
        if name and qq != "all":
            data["name"] = name
            
        return {
            "type": MessageSegmentType.AT,
            "data": data
        }
    
    @staticmethod
    def at_all() -> Dict[str, Any]:
        """
        @全体成员消息段
        
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.AT,
            "data": {
                "qq": "all"
            }
        }
    
    @staticmethod
    def rps() -> Dict[str, Any]:
        """
        猜拳魔法表情
        
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.RPS,
            "data": {}
        }
    
    @staticmethod
    def dice() -> Dict[str, Any]:
        """
        掷骰子魔法表情
        
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.DICE,
            "data": {}
        }
    
    @staticmethod
    def shake() -> Dict[str, Any]:
        """
        窗口抖动（戳一戳）
        
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.SHAKE,
            "data": {}
        }
    
    @staticmethod
    def poke(type: Union[int, str], id: Union[int, str]) -> Dict[str, Any]:
        """
        戳一戳
        
        :param type: 类型
        :param id: ID
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.POKE,
            "data": {
                "type": str(type),
                "id": str(id)
            }
        }
    
    @staticmethod
    def anonymous(ignore: bool = False) -> Dict[str, Any]:
        """
        匿名发消息
        
        :param ignore: 是否强制发送
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.ANONYMOUS,
            "data": {
                "ignore": ignore
            }
        }
    
    @staticmethod
    def share(url: str, title: str, content: Optional[str] = None, image: Optional[str] = None) -> Dict[str, Any]:
        """
        链接分享
        
        :param url: 链接
        :param title: 标题
        :param content: 内容描述
        :param image: 图片URL
        :return: 消息段字典
        """
        data = {
            "url": url,
            "title": title
        }
        
        if content:
            data["content"] = content
        if image:
            data["image"] = image
            
        return {
            "type": MessageSegmentType.SHARE,
            "data": data
        }
    
    @staticmethod
    def contact(type: str, id: Union[int, str]) -> Dict[str, Any]:
        """
        推荐好友/群
        
        :param type: 类型，group或qq
        :param id: 推荐的QQ号或群号
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.CONTACT,
            "data": {
                "type": type,
                "id": str(id)
            }
        }
    
    @staticmethod
    def location(lat: float, lon: float, title: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
        """
        位置
        
        :param lat: 纬度
        :param lon: 经度
        :param title: 标题
        :param content: 内容描述
        :return: 消息段字典
        """
        data = {
            "lat": lat,
            "lon": lon
        }
        
        if title:
            data["title"] = title
        if content:
            data["content"] = content
            
        return {
            "type": MessageSegmentType.LOCATION,
            "data": data
        }
    
    @staticmethod
    def music(type: str, id: Union[int, str]) -> Dict[str, Any]:
        """
        音乐分享
        
        :param type: 类型，qq、163、xm分别表示QQ音乐、网易云音乐、虾米音乐
        :param id: 歌曲ID
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.MUSIC,
            "data": {
                "type": type,
                "id": str(id)
            }
        }
    
    @staticmethod
    def music_custom(url: str, audio: str, title: str, 
                    content: Optional[str] = None, 
                    image: Optional[str] = None) -> Dict[str, Any]:
        """
        自定义音乐分享
        
        :param url: 点击后跳转的链接
        :param audio: 音乐URL
        :param title: 标题
        :param content: 内容描述
        :param image: 图片URL
        :return: 消息段字典
        """
        data = {
            "type": "custom",
            "url": url,
            "audio": audio,
            "title": title
        }
        
        if content:
            data["content"] = content
        if image:
            data["image"] = image
            
        return {
            "type": MessageSegmentType.MUSIC,
            "data": data
        }
    
    @staticmethod
    def reply(id: Union[int, str]) -> Dict[str, Any]:
        """
        回复
        
        :param id: 回复的消息ID
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.REPLY,
            "data": {
                "id": str(id)
            }
        }
    
    @staticmethod
    def forward(id: str) -> Dict[str, Any]:
        """
        合并转发
        
        :param id: 合并转发ID
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.FORWARD,
            "data": {
                "id": id
            }
        }
    
    @staticmethod
    def node(id: Union[int, str]) -> Dict[str, Any]:
        """
        合并转发节点
        
        :param id: 转发的消息ID
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.NODE,
            "data": {
                "id": str(id)
            }
        }
    
    @staticmethod
    def node_custom(user_id: Union[int, str], nickname: str, content: Union[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        自定义合并转发节点
        
        :param user_id: 发送者QQ号
        :param nickname: 发送者昵称
        :param content: 消息内容，可以是文本或消息段列表
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.NODE,
            "data": {
                "user_id": str(user_id),
                "nickname": nickname,
                "content": content
            }
        }
    
    @staticmethod
    def xml(data: str) -> Dict[str, Any]:
        """
        XML消息
        
        :param data: XML内容
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.XML,
            "data": {
                "data": data
            }
        }
    
    @staticmethod
    def json(data: Union[str, Dict]) -> Dict[str, Any]:
        """
        JSON消息
        
        :param data: JSON内容，可以是字符串或字典
        :return: 消息段字典
        """
        if isinstance(data, dict):
            data = json.dumps(data)
            
        return {
            "type": MessageSegmentType.JSON,
            "data": {
                "data": data
            }
        }
    
    @staticmethod
    def card_image(file: Union[str, Path, bytes], 
                  minwidth: Optional[int] = None, 
                  minheight: Optional[int] = None, 
                  maxwidth: Optional[int] = None, 
                  maxheight: Optional[int] = None, 
                  source: Optional[str] = None, 
                  icon: Optional[str] = None) -> Dict[str, Any]:
        """
        卡片图片
        
        :param file: 图片文件名、路径、URL或图片bytes数据
        :param minwidth: 最小宽度
        :param minheight: 最小高度
        :param maxwidth: 最大宽度
        :param maxheight: 最大高度
        :param source: 图片来源
        :param icon: 图标URL
        :return: 消息段字典
        """
        data = {}
        
        if isinstance(file, bytes):
            data["file"] = f"base64://{base64.b64encode(file).decode()}"
        elif isinstance(file, (str, Path)) and os.path.exists(str(file)):
            with open(str(file), "rb") as f:
                data["file"] = f"base64://{base64.b64encode(f.read()).decode()}"
        else:
            data["file"] = str(file)
            
        if minwidth:
            data["minwidth"] = minwidth
        if minheight:
            data["minheight"] = minheight
        if maxwidth:
            data["maxwidth"] = maxwidth
        if maxheight:
            data["maxheight"] = maxheight
        if source:
            data["source"] = source
        if icon:
            data["icon"] = icon
            
        return {
            "type": MessageSegmentType.CARD_IMAGE,
            "data": data
        }
    
    @staticmethod
    def tts(text: str) -> Dict[str, Any]:
        """
        文本转语音
        
        :param text: 要转换的文本
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.TTS,
            "data": {
                "text": text
            }
        }
    
    @staticmethod
    def file(file: Union[str, Path]) -> Dict[str, Any]:
        """
        文件消息
        
        :param file: 文件路径
        :return: 消息段字典
        """
        return {
            "type": MessageSegmentType.FILE,
            "data": {
                "file": str(file)
            }
        }


class Message:
    """
    消息构建器，用于生成符合napcat API的消息格式
    """
    
    def __init__(self):
        self.segments: List[Dict[str, Any]] = []
    
    def __str__(self) -> str:
        """
        将消息段列表转换为CQ码字符串或JSON字符串，用于调试
        
        :return: 表示消息内容的字符串
        """
        return json.dumps(self.segments, ensure_ascii=False)
    
    def append(self, segment: Dict[str, Any]) -> "Message":
        """
        添加一个消息段
        
        :param segment: 消息段
        :return: 消息构建器本身
        """
        self.segments.append(segment)
        return self
    
    def extend(self, segments: List[Dict[str, Any]]) -> "Message":
        """
        添加多个消息段
        
        :param segments: 消息段列表
        :return: 消息构建器本身
        """
        self.segments.extend(segments)
        return self
    
    def text(self, text: str) -> "Message":
        """
        添加文本消息段
        
        :param text: 文本内容
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.text(text))
    
    def face(self, id: int) -> "Message":
        """
        添加表情消息段
        
        :param id: 表情ID
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.face(id))
    
    def image(self, file: Union[str, Path, bytes], **kwargs) -> "Message":
        """
        添加图片消息段
        
        :param file: 图片文件名、路径、URL或图片bytes数据
        :param kwargs: 其他参数
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.image(file, **kwargs))
    
    def record(self, file: Union[str, Path, bytes], **kwargs) -> "Message":
        """
        添加语音消息段
        
        :param file: 语音文件名、路径、URL或语音bytes数据
        :param kwargs: 其他参数
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.record(file, **kwargs))
    
    def video(self, file: Union[str, Path, bytes], **kwargs) -> "Message":
        """
        添加视频消息段
        
        :param file: 视频文件名、路径、URL或视频bytes数据
        :param kwargs: 其他参数
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.video(file, **kwargs))
    
    def at(self, qq: Union[int, str], name: Optional[str] = None) -> "Message":
        """
        添加@某人消息段
        
        :param qq: 被@的QQ号
        :param name: 自定义@的昵称
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.at(qq, name))
    
    def at_all(self) -> "Message":
        """
        添加@全体成员消息段
        
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.at_all())
    
    def rps(self) -> "Message":
        """
        添加猜拳魔法表情
        
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.rps())
    
    def dice(self) -> "Message":
        """
        添加掷骰子魔法表情
        
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.dice())
    
    def shake(self) -> "Message":
        """
        添加窗口抖动（戳一戳）
        
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.shake())
    
    def poke(self, type: Union[int, str], id: Union[int, str]) -> "Message":
        """
        添加戳一戳
        
        :param type: 类型
        :param id: ID
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.poke(type, id))
    
    def anonymous(self, ignore: bool = False) -> "Message":
        """
        添加匿名发消息
        
        :param ignore: 是否强制发送
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.anonymous(ignore))
    
    def share(self, url: str, title: str, **kwargs) -> "Message":
        """
        添加链接分享
        
        :param url: 链接
        :param title: 标题
        :param kwargs: 其他参数
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.share(url, title, **kwargs))
    
    def contact(self, type: str, id: Union[int, str]) -> "Message":
        """
        添加推荐好友/群
        
        :param type: 类型
        :param id: QQ号或群号
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.contact(type, id))
    
    def location(self, lat: float, lon: float, **kwargs) -> "Message":
        """
        添加位置
        
        :param lat: 纬度
        :param lon: 经度
        :param kwargs: 其他参数
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.location(lat, lon, **kwargs))
    
    def music(self, type: str, id: Union[int, str]) -> "Message":
        """
        添加音乐分享
        
        :param type: 类型
        :param id: 音乐ID
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.music(type, id))
    
    def music_custom(self, url: str, audio: str, title: str, **kwargs) -> "Message":
        """
        添加自定义音乐分享
        
        :param url: 点击后跳转的链接
        :param audio: 音乐URL
        :param title: 标题
        :param kwargs: 其他参数
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.music_custom(url, audio, title, **kwargs))
    
    def reply(self, id: Union[int, str]) -> "Message":
        """
        添加回复
        
        :param id: 回复的消息ID
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.reply(id))
    
    def forward(self, id: str) -> "Message":
        """
        添加合并转发
        
        :param id: 合并转发ID
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.forward(id))
    
    def node(self, id: Union[int, str]) -> "Message":
        """
        添加合并转发节点
        
        :param id: 转发的消息ID
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.node(id))
    
    def node_custom(self, user_id: Union[int, str], nickname: str, content: Union[str, List[Dict[str, Any]]]) -> "Message":
        """
        添加自定义合并转发节点
        
        :param user_id: 发送者QQ号
        :param nickname: 发送者昵称
        :param content: 消息内容
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.node_custom(user_id, nickname, content))
    
    def xml(self, data: str) -> "Message":
        """
        添加XML消息
        
        :param data: XML内容
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.xml(data))
    
    def json(self, data: Union[str, Dict]) -> "Message":
        """
        添加JSON消息
        
        :param data: JSON内容
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.json(data))
    
    def card_image(self, file: Union[str, Path, bytes], **kwargs) -> "Message":
        """
        添加卡片图片
        
        :param file: 图片文件名、路径、URL或图片bytes数据
        :param kwargs: 其他参数
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.card_image(file, **kwargs))
    
    def tts(self, text: str) -> "Message":
        """
        添加文本转语音
        
        :param text: 要转换的文本
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.tts(text))
    
    def file(self, file: Union[str, Path]) -> "Message":
        """
        添加文件消息
        
        :param file: 文件路径
        :return: 消息构建器本身
        """
        return self.append(MessageSegment.file(file))
    
    def get_segments(self) -> List[Dict[str, Any]]:
        """
        获取消息段列表
        
        :return: 消息段列表
        """
        return self.segments
    
    def string(self) -> str:
        """
        转换为适合API调用的字符串
        
        :return: JSON字符串或CQ码字符串
        """
        return json.dumps(self.segments)
    
    @classmethod
    def from_segments(cls, segments: List[Dict[str, Any]]) -> "Message":
        """
        从消息段列表创建消息
        
        :param segments: 消息段列表
        :return: 消息构建器
        """
        msg = cls()
        msg.extend(segments)
        return msg
    
    @classmethod
    def from_raw_message(cls, message: str) -> "Message":
        """
        从原始消息文本创建消息
        
        :param message: 原始消息文本
        :return: 消息构建器
        """
        msg = cls()
        msg.text(message)
        return msg