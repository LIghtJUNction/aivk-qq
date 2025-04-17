from typing import Dict, Union, Optional, Any, List
from pathlib import Path



class MessageSegment:
    """
    消息段工厂类，提供各种类型消息段的构建方法
    
    所有方法返回符合OneBot标准的消息段字典结构：
    {
        "type": "消息类型",
        "data": { ...消息内容 }
    }
    """

    @staticmethod
    def face(id: int) -> Dict[str, Any]:
        """
        QQ表情消息段
        
        :param id: 表情ID，0~311为标准表情，具体映射关系参考：
                  https://github.com/kyubotics/coolq-http-api/wiki/表情ID表
        :return: 包含表情ID的消息段字典
        """

    @staticmethod
    def image(file: Union[str, Path, bytes],
              type: Optional[str] = None,
              url: Optional[str] = None,
              cache: bool = True,
              proxy: bool = True,
              timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        构建图片消息段，支持多种输入格式和高级参数
        
        :param file: 图片资源，支持以下类型：
                    - 文件路径字符串或Path对象
                    - HTTP/HTTPS URL
                    - bytes类型的图片数据
        :param type: 图片类型特殊标识，可选值：
                   - "flash" 表示闪照（仅限好友私聊）
        :param url: 图片网络URL，当file参数为本地路径时生效
        :param cache: 是否缓存网络图片，默认为True
        :param proxy: 是否通过代理服务器下载，默认为True
        :param timeout: 下载超时时间（秒），None表示使用默认值
        :return: 图片消息段字典
        
        :raises FileNotFoundError: 当本地文件不存在时抛出
        """
        # TODO

class Message:
    """
    消息构建器类，支持链式添加各种消息段
    """
    def __init__(self) -> None: ...
    def text(self, content: str) -> "Message": ...
    def image(self, file: Union[str, Path, bytes], type: Optional[str] = None,
              url: Optional[str] = None, cache: bool = True,
              proxy: bool = True, timeout: Optional[int] = None) -> "Message": ...
    def record(self, file: Union[str, Path, bytes], magic: bool = False,
               cache: bool = True, proxy: bool = True, timeout: Optional[int] = None) -> "Message": ...
    def video(self, file: Union[str, Path, bytes], cache: bool = True,
              proxy: bool = True, timeout: Optional[int] = None) -> "Message": ...
    def share(self, url: str, title: str,
              content: Optional[str] = None, image: Optional[str] = None) -> "Message": ...
    def location(self, lat: float, lon: float,
                 title: Optional[str] = None, content: Optional[str] = None) -> "Message": ...
    def music(self, music_type: str, music_id: Union[int, str]) -> "Message": ...
    def music_custom(self, url: str, audio: str, title: str,
                     content: Optional[str] = None, image: Optional[str] = None) -> "Message": ...
    def face(self, face_id: int) -> "Message": ...
    def at(self, user_id: Union[int, str], name: Optional[str] = None) -> "Message": ...
    def at_all(self) -> "Message": ...
    def reply(self, message_id: Union[int, str]) -> "Message": ...
    def get_segments(self) -> List[Dict[str, Any]]: ...
    @staticmethod
    def from_cq_str(cq: str) -> "Message": ...
    @staticmethod
    def from_segments(segments: List[Dict[str, Any]]) -> "Message": ...
    def extract_plain_text(self) -> str: ...

