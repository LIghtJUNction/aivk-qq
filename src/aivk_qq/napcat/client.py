from typing import Dict, List, Union, Optional, Any, Literal
import time
import asyncio
import json
import logging
from ..base.message import Message

logger = logging.getLogger("aivk.qq.napcat.client")

class NapcatClient:
    """
    NapCat API客户端，提供对NapCat API的全面封装
    """
    def __init__(self, api):
        """
        初始化NapCat客户端
        
        :param api: NapcatAPI实例，用于处理底层通信
        """
        self.api = api
    
    # ==================== 基础辅助方法 ====================
    
    async def _call_api(self, action: str, **params) -> Dict[str, Any]:
        """
        内部方法，调用NapCat API
        
        :param action: API动作名称
        :param params: API参数
        :return: API响应
        """
        if not self.api.ws_connection:
            raise Exception("WebSocket连接未建立，请先连接")
        
        api_data = {
            "action": action,
            "params": params,
            "echo": f"{action}_{int(time.time())}"
        }
        
        # 发送请求
        await self.api.ws_connection.send(json.dumps(api_data))
        logger.debug(f"已发送API请求: {action}")
        
        # 接收响应
        try:
            response = await asyncio.wait_for(self.api.ws_connection.recv(), timeout=10.0)
            response_data = json.loads(response)
            logger.debug(f"接收到API响应: {response_data}")
            return response_data
        except Exception as e:
            logger.error(f"API调用失败 ({action}): {str(e)}")
            raise Exception(f"API调用失败: {str(e)}")

    def _handle_message(self, message) -> Union[str, List, Dict]:
        """
        处理消息参数，支持Message对象、字符串或消息段列表
        
        :param message: 消息内容，可以是Message对象、字符串或消息段列表
        :return: 处理后的消息，适合API调用
        """
        if isinstance(message, Message):
            return message.get_segments()
        elif isinstance(message, str):
            return message
        elif isinstance(message, list):
            return message
        elif isinstance(message, dict):
            # 单个消息段
            return [message]
        else:
            raise TypeError("消息类型必须是Message对象、字符串、字典或列表")
    
    # ==================== 账号相关API ====================
    
    async def get_login_info(self) -> Dict[str, Any]:
        """
        获取登录号信息
        
        :return: 包含QQ号、昵称等信息的字典
        """
        return await self._call_api("get_login_info")
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        获取账号信息
        
        :return: 账号详细信息
        """
        return await self._call_api("get_account_info")
    
    async def set_account_info(self, nickname: Optional[str] = None, company: Optional[str] = None, 
                              email: Optional[str] = None, college: Optional[str] = None, 
                              personal_note: Optional[str] = None) -> Dict[str, Any]:
        """
        设置账号信息
        
        :param nickname: 昵称
        :param company: 公司
        :param email: 邮箱
        :param college: 大学
        :param personal_note: 个人说明
        :return: 操作结果
        """
        params = {}
        if nickname:
            params["nickname"] = nickname
        if company:
            params["company"] = company
        if email:
            params["email"] = email
        if college:
            params["college"] = college
        if personal_note:
            params["personal_note"] = personal_note
        
        return await self._call_api("set_account_info", **params)
    
    async def set_signature(self, signature: str) -> Dict[str, Any]:
        """
        设置个性签名
        
        :param signature: 签名内容
        :return: 操作结果
        """
        return await self._call_api("set_signature", signature=signature)
    
    async def get_friend_list(self) -> List[Dict[str, Any]]:
        """
        获取好友列表
        
        :return: 好友列表
        """
        result = await self._call_api("get_friend_list")
        return result.get("data", [])
    
    async def get_friend_group_list(self) -> List[Dict[str, Any]]:
        """
        获取好友分组列表
        
        :return: 好友分组列表
        """
        result = await self._call_api("get_friend_group_list")
        return result.get("data", [])
    
    async def get_stranger_info(self, user_id: Union[int, str], no_cache: bool = False) -> Dict[str, Any]:
        """
        获取陌生人信息
        
        :param user_id: QQ号
        :param no_cache: 是否不使用缓存
        :return: 陌生人信息
        """
        return await self._call_api("get_stranger_info", user_id=user_id, no_cache=no_cache)
    
    async def get_user_status(self, user_id: Union[int, str]) -> Dict[str, Any]:
        """
        获取用户状态
        
        :param user_id: QQ号
        :return: 用户状态信息
        """
        return await self._call_api("get_user_status", user_id=user_id)
    
    async def get_online_clients(self) -> List[Dict[str, Any]]:
        """
        获取当前账号在线客户端列表
        
        :return: 在线客户端列表
        """
        result = await self._call_api("get_online_clients")
        return result.get("data", [])
    
    async def set_online_status(self, status: Union[int, str]) -> Dict[str, Any]:
        """
        设置在线状态
        
        :param status: 状态值
            - 11: 离线
            - 31: 在线
            - 41: 离开
            - 50: 请勿打扰
            - 60: 隐身
            - 70: 忙碌
        :return: 操作结果
        """
        return await self._call_api("set_online_status", status=status)
    
    async def set_custom_online_status(self, online_status: Union[int, str], 
                                      title: str, 
                                      subtitle: Optional[str] = None) -> Dict[str, Any]:
        """
        设置自定义在线状态
        
        :param online_status: 在线状态代码
        :param title: 状态标题
        :param subtitle: 状态子标题
        :return: 操作结果
        """
        params = {
            "online_status": online_status,
            "title": title
        }
        if subtitle:
            params["subtitle"] = subtitle
        
        return await self._call_api("set_custom_online_status", **params)
    
    async def delete_friend(self, user_id: Union[int, str]) -> Dict[str, Any]:
        """
        删除好友
        
        :param user_id: 好友QQ号
        :return: 操作结果
        """
        return await self._call_api("delete_friend", user_id=user_id)
    
    async def handle_friend_request(self, flag: str, approve: bool = True, remark: Optional[str] = None) -> Dict[str, Any]:
        """
        处理好友请求
        
        :param flag: 请求标识，收到好友请求事件时获得
        :param approve: 是否同意请求
        :param remark: 添加后的好友备注（仅当approve=True时有效）
        :return: 操作结果
        """
        params = {
            "flag": flag,
            "approve": approve
        }
        if approve and remark:
            params["remark"] = remark
        
        return await self._call_api("set_friend_add_request", **params)
    
    async def poke(self, target_id: Union[int, str], group_id: Optional[Union[int, str]] = None) -> Dict[str, Any]:
        """
        发送戳一戳
        
        :param target_id: 目标QQ号
        :param group_id: 群号，如果指定，则在群聊中戳一戳
        :return: 操作结果
        """
        params = {"target_id": target_id}
        if group_id:
            params["group_id"] = group_id
            
        return await self._call_api("poke", **params)
    
    async def set_group_note(self, group_id: Union[int, str], name: str) -> Dict[str, Any]:
        """
        设置群备注
        
        :param group_id: 群号
        :param name: 备注名
        :return: 操作结果
        """
        return await self._call_api("set_group_note", group_id=group_id, name=name)
    
    async def get_recent_message_list(self) -> List[Dict[str, Any]]:
        """
        获取最近消息列表（每个会话最新的一条消息）
        
        :return: 最近消息列表
        """
        result = await self._call_api("get_recent_message_list")
        return result.get("data", [])
    
    async def like(self, user_id: Union[int, str], times: int = 1) -> Dict[str, Any]:
        """
        点赞操作
        
        :param user_id: 目标QQ号
        :param times: 点赞次数，默认1次
        :return: 操作结果
        """
        return await self._call_api("like", user_id=user_id, times=times)
    
    async def get_like_list(self) -> List[Dict[str, Any]]:
        """
        获取点赞列表
        
        :return: 点赞列表
        """
        result = await self._call_api("get_like_list")
        return result.get("data", [])
    
    # ==================== 消息相关API ====================

    async def send_private_msg(self, user_id: Union[int, str], 
                              message: Union[str, Message, List, Dict], 
                              auto_escape: bool = False) -> Dict[str, Any]:
        """
        发送私聊消息
        
        :param user_id: 目标QQ号
        :param message: 消息内容，可以是字符串、Message对象或消息段列表
        :param auto_escape: 是否不解析CQ码，默认为False
        :return: 包含message_id的字典
        """
        return await self._call_api("send_private_msg", 
                                   user_id=user_id, 
                                   message=self._handle_message(message), 
                                   auto_escape=auto_escape)
    
    async def send_group_msg(self, group_id: Union[int, str], 
                            message: Union[str, Message, List, Dict], 
                            auto_escape: bool = False) -> Dict[str, Any]:
        """
        发送群消息
        
        :param group_id: 群号
        :param message: 消息内容，可以是字符串、Message对象或消息段列表
        :param auto_escape: 是否不解析CQ码，默认为False
        :return: 包含message_id的字典
        """
        return await self._call_api("send_group_msg", 
                                   group_id=group_id, 
                                   message=self._handle_message(message), 
                                   auto_escape=auto_escape)
    
    async def send_msg(self, message: Union[str, Message, List, Dict], 
                      message_type: Literal["private", "group"],
                      user_id: Optional[Union[int, str]] = None,
                      group_id: Optional[Union[int, str]] = None,
                      auto_escape: bool = False) -> Dict[str, Any]:
        """
        发送消息
        
        :param message: 消息内容，可以是字符串、Message对象或消息段列表
        :param message_type: 消息类型，可以是"private"或"group"
        :param user_id: 目标QQ号（当message_type为"private"时必须）
        :param group_id: 群号（当message_type为"group"时必须）
        :param auto_escape: 是否不解析CQ码，默认为False
        :return: 包含message_id的字典
        """
        params = {
            "message_type": message_type,
            "message": self._handle_message(message),
            "auto_escape": auto_escape
        }
        
        if message_type == "private":
            if user_id is None:
                raise ValueError("发送私聊消息时必须提供user_id")
            params["user_id"] = user_id
        elif message_type == "group":
            if group_id is None:
                raise ValueError("发送群消息时必须提供group_id")
            params["group_id"] = group_id
        else:
            raise ValueError("message_type必须是'private'或'group'")
        
        return await self._call_api("send_msg", **params)
    
    async def recall_msg(self, message_id: Union[int, str]) -> Dict[str, Any]:
        """
        撤回消息
        
        :param message_id: 消息ID
        :return: 操作结果
        """
        return await self._call_api("delete_msg", message_id=message_id)
    
    async def get_msg(self, message_id: Union[int, str]) -> Dict[str, Any]:
        """
        获取消息详情
        
        :param message_id: 消息ID
        :return: 消息详情
        """
        return await self._call_api("get_msg", message_id=message_id)
    
    async def get_group_history_msg(self, group_id: Union[int, str], 
                                   message_seq: Optional[int] = None,
                                   count: int = 20) -> List[Dict[str, Any]]:
        """
        获取群历史消息
        
        :param group_id: 群号
        :param message_seq: 起始消息序号，默认从最新消息开始
        :param count: 获取消息数量，默认20
        :return: 消息列表
        """
        params = {
            "group_id": group_id,
            "count": count
        }
        if message_seq is not None:
            params["message_seq"] = message_seq
            
        result = await self._call_api("get_group_msg_history", **params)
        return result.get("data", {}).get("messages", [])
    
    async def get_private_history_msg(self, user_id: Union[int, str], 
                                     message_seq: Optional[int] = None,
                                     count: int = 20) -> List[Dict[str, Any]]:
        """
        获取私聊历史消息
        
        :param user_id: QQ号
        :param message_seq: 起始消息序号，默认从最新消息开始
        :param count: 获取消息数量，默认20
        :return: 消息列表
        """
        params = {
            "user_id": user_id,
            "count": count
        }
        if message_seq is not None:
            params["message_seq"] = message_seq
            
        result = await self._call_api("get_friend_msg_history", **params)
        return result.get("data", {}).get("messages", [])
    
    async def mark_msg_as_read(self, message_id: Union[int, str]) -> Dict[str, Any]:
        """
        标记消息为已读
        
        :param message_id: 消息ID
        :return: 操作结果
        """
        return await self._call_api("mark_msg_as_read", message_id=message_id)
    
    async def set_private_msg_read(self, user_id: Union[int, str]) -> Dict[str, Any]:
        """
        标记私聊所有消息为已读
        
        :param user_id: QQ号
        :return: 操作结果
        """
        return await self._call_api("set_friend_add_request", user_id=user_id)
    
    async def set_group_msg_read(self, group_id: Union[int, str]) -> Dict[str, Any]:
        """
        标记群聊所有消息为已读
        
        :param group_id: 群号
        :return: 操作结果
        """
        return await self._call_api("set_group_msg_read", group_id=group_id)
    
    async def get_forward_msg(self, id: str) -> Dict[str, Any]:
        """
        获取合并转发消息
        
        :param id: 合并转发ID
        :return: 合并转发消息详情
        """
        return await self._call_api("get_forward_msg", id=id)
    
    async def set_typing(self, user_id: Union[int, str], action: Optional[Literal[0, 1, 2, 3]] = 1) -> Dict[str, Any]:
        """
        设置输入状态
        
        :param user_id: 目标QQ号
        :param action: 输入状态
            - 0: 取消输入
            - 1: 文本输入中
            - 2: 语音输入中
            - 3: 图片输入中
        :return: 操作结果
        """
        return await self._call_api("set_typing", user_id=user_id, action=action)
    
    # ==================== 图片和语音相关API ====================
    
    async def get_image(self, file: str) -> Dict[str, Any]:
        """
        获取图片信息
        
        :param file: 图片缓存文件名
        :return: 图片信息
        """
        return await self._call_api("get_image", file=file)
    
    async def ocr_image(self, image: str) -> Dict[str, Any]:
        """
        识别图片中的文字
        
        :param image: 图片ID
        :return: OCR结果
        """
        return await self._call_api("ocr_image", image=image)
        
    async def can_send_image(self) -> bool:
        """
        检查是否可以发送图片
        
        :return: 是否可以发送图片
        """
        result = await self._call_api("can_send_image")
        return result.get("data", {}).get("yes", False)
    
    async def can_send_record(self) -> bool:
        """
        检查是否可以发送语音
        
        :return: 是否可以发送语音
        """
        result = await self._call_api("can_send_record")
        return result.get("data", {}).get("yes", False)
    
    async def get_voice(self, file: str, out_format: Optional[str] = None) -> Dict[str, Any]:
        """
        获取语音信息
        
        :param file: 语音文件
        :param out_format: 输出格式，默认为mp3
        :return: 语音信息
        """
        params = {"file": file}
        if out_format:
            params["out_format"] = out_format
            
        return await self._call_api("get_record", **params)
    
    # ==================== 群相关API ====================
    
    async def get_group_info(self, group_id: Union[int, str], no_cache: bool = False) -> Dict[str, Any]:
        """
        获取群信息
        
        :param group_id: 群号
        :param no_cache: 是否不使用缓存
        :return: 群信息
        """
        return await self._call_api("get_group_info", group_id=group_id, no_cache=no_cache)
    
    async def get_group_list(self) -> List[Dict[str, Any]]:
        """
        获取群列表
        
        :return: 群列表
        """
        result = await self._call_api("get_group_list")
        return result.get("data", [])
    
    async def get_group_member_info(self, group_id: Union[int, str], 
                                   user_id: Union[int, str], 
                                   no_cache: bool = False) -> Dict[str, Any]:
        """
        获取群成员信息
        
        :param group_id: 群号
        :param user_id: QQ号
        :param no_cache: 是否不使用缓存
        :return: 群成员信息
        """
        return await self._call_api("get_group_member_info", 
                                   group_id=group_id, 
                                   user_id=user_id, 
                                   no_cache=no_cache)
    
    async def get_group_member_list(self, group_id: Union[int, str]) -> List[Dict[str, Any]]:
        """
        获取群成员列表
        
        :param group_id: 群号
        :return: 群成员列表
        """
        result = await self._call_api("get_group_member_list", group_id=group_id)
        return result.get("data", [])
    
    async def set_group_name(self, group_id: Union[int, str], name: str) -> Dict[str, Any]:
        """
        设置群名
        
        :param group_id: 群号
        :param name: 新群名
        :return: 操作结果
        """
        return await self._call_api("set_group_name", group_id=group_id, name=name)
    
    async def set_group_avatar(self, group_id: Union[int, str], file: str) -> Dict[str, Any]:
        """
        设置群头像
        
        :param group_id: 群号
        :param file: 图片文件路径或URL
        :return: 操作结果
        """
        return await self._call_api("set_group_portrait", group_id=group_id, file=file)
    
    async def set_group_card(self, group_id: Union[int, str], 
                            user_id: Union[int, str], 
                            card: str = "") -> Dict[str, Any]:
        """
        设置群成员名片
        
        :param group_id: 群号
        :param user_id: QQ号
        :param card: 名片内容，空字符串表示删除名片
        :return: 操作结果
        """
        return await self._call_api("set_group_card", 
                                   group_id=group_id, 
                                   user_id=user_id, 
                                   card=card)
    
    async def set_group_admin(self, group_id: Union[int, str], 
                             user_id: Union[int, str], 
                             enable: bool = True) -> Dict[str, Any]:
        """
        设置群管理员
        
        :param group_id: 群号
        :param user_id: QQ号
        :param enable: 是否设置为管理员
        :return: 操作结果
        """
        return await self._call_api("set_group_admin", 
                                   group_id=group_id, 
                                   user_id=user_id, 
                                   enable=enable)
    
    async def set_group_special_title(self, group_id: Union[int, str], 
                                     user_id: Union[int, str], 
                                     special_title: str = "", 
                                     duration: int = -1) -> Dict[str, Any]:
        """
        设置群成员专属头衔
        
        :param group_id: 群号
        :param user_id: QQ号
        :param special_title: 专属头衔，空字符串表示删除专属头衔
        :param duration: 有效期，单位秒，-1表示永久
        :return: 操作结果
        """
        return await self._call_api("set_group_special_title", 
                                   group_id=group_id, 
                                   user_id=user_id, 
                                   special_title=special_title, 
                                   duration=duration)
    
    async def set_group_ban(self, group_id: Union[int, str], 
                           user_id: Union[int, str], 
                           duration: int = 30 * 60) -> Dict[str, Any]:
        """
        群单人禁言
        
        :param group_id: 群号
        :param user_id: QQ号
        :param duration: 禁言时长，单位秒，0表示解除禁言
        :return: 操作结果
        """
        return await self._call_api("set_group_ban", 
                                   group_id=group_id, 
                                   user_id=user_id, 
                                   duration=duration)
    
    async def set_group_whole_ban(self, group_id: Union[int, str], enable: bool = True) -> Dict[str, Any]:
        """
        群全体禁言
        
        :param group_id: 群号
        :param enable: 是否开启
        :return: 操作结果
        """
        return await self._call_api("set_group_whole_ban", group_id=group_id, enable=enable)
    
    async def kick_group_member(self, group_id: Union[int, str], 
                               user_id: Union[int, str], 
                               reject_add_request: bool = False) -> Dict[str, Any]:
        """
        踢出群成员
        
        :param group_id: 群号
        :param user_id: QQ号
        :param reject_add_request: 是否拒绝此人的加群请求
        :return: 操作结果
        """
        return await self._call_api("set_group_kick", 
                                   group_id=group_id, 
                                   user_id=user_id, 
                                   reject_add_request=reject_add_request)
    
    async def leave_group(self, group_id: Union[int, str], is_dismiss: bool = False) -> Dict[str, Any]:
        """
        退出群组
        
        :param group_id: 群号
        :param is_dismiss: 是否解散群（仅群主可用）
        :return: 操作结果
        """
        return await self._call_api("set_group_leave", group_id=group_id, is_dismiss=is_dismiss)
    
    async def handle_group_request(self, flag: str, 
                                  sub_type: Literal["add", "invite"], 
                                  approve: bool = True, 
                                  reason: str = "") -> Dict[str, Any]:
        """
        处理加群请求/邀请
        
        :param flag: 请求标识，收到加群请求或邀请事件时获得
        :param sub_type: 请求类型，"add"为加群请求，"invite"为邀请
        :param approve: 是否同意
        :param reason: 拒绝理由（仅当approve=False时有效）
        :return: 操作结果
        """
        return await self._call_api("set_group_add_request", 
                                   flag=flag, 
                                   sub_type=sub_type, 
                                   approve=approve, 
                                   reason=reason)
    
    async def get_group_honor_info(self, group_id: Union[int, str], 
                                  type: Literal["talkative", "performer", "legend", "strong_newbie", "emotion", "all"] = "all") -> Dict[str, Any]:
        """
        获取群荣誉信息
        
        :param group_id: 群号
        :param type: 要获取的群荣誉类型，可以是 "talkative" "performer" "legend" "strong_newbie" "emotion" "all"
        :return: 群荣誉信息
        """
        return await self._call_api("get_group_honor_info", group_id=group_id, type=type)
    
    async def get_group_system_msg(self) -> Dict[str, Any]:
        """
        获取群系统消息
        
        :return: 群系统消息
        """
        return await self._call_api("get_group_system_msg")
    
    async def get_essence_msg_list(self, group_id: Union[int, str]) -> List[Dict[str, Any]]:
        """
        获取精华消息列表
        
        :param group_id: 群号
        :return: 精华消息列表
        """
        result = await self._call_api("get_essence_msg_list", group_id=group_id)
        return result.get("data", [])
    
    async def set_essence_msg(self, message_id: Union[int, str]) -> Dict[str, Any]:
        """
        设置精华消息
        
        :param message_id: 消息ID
        :return: 操作结果
        """
        return await self._call_api("set_essence_msg", message_id=message_id)
    
    async def delete_essence_msg(self, message_id: Union[int, str]) -> Dict[str, Any]:
        """
        删除精华消息
        
        :param message_id: 消息ID
        :return: 操作结果
        """
        return await self._call_api("delete_essence_msg", message_id=message_id)
    
    async def get_group_at_all_remain(self, group_id: Union[int, str]) -> Dict[str, Any]:
        """
        获取群 @全体成员 剩余次数
        
        :param group_id: 群号
        :return: 剩余次数
        """
        return await self._call_api("get_group_at_all_remain", group_id=group_id)
    
    # ==================== 文件相关API ====================
    
    async def upload_group_file(self, group_id: Union[int, str], 
                               file: str, 
                               name: str, 
                               folder: str = "") -> Dict[str, Any]:
        """
        上传群文件
        
        :param group_id: 群号
        :param file: 本地文件路径
        :param name: 文件名
        :param folder: 父目录ID，默认根目录
        :return: 上传结果
        """
        return await self._call_api("upload_group_file", 
                                   group_id=group_id, 
                                   file=file, 
                                   name=name, 
                                   folder=folder)
    
    async def upload_private_file(self, user_id: Union[int, str], 
                                file: str, 
                                name: str) -> Dict[str, Any]:
        """
        上传私聊文件
        
        :param user_id: 对方QQ号
        :param file: 本地文件路径
        :param name: 文件名
        :return: 上传结果
        """
        return await self._call_api("upload_private_file", 
                                   user_id=user_id, 
                                   file=file, 
                                   name=name)
    
    async def delete_group_file(self, group_id: Union[int, str], file_id: str) -> Dict[str, Any]:
        """
        删除群文件
        
        :param group_id: 群号
        :param file_id: 文件ID
        :return: 操作结果
        """
        return await self._call_api("delete_group_file", group_id=group_id, file_id=file_id)
    
    async def create_group_file_folder(self, group_id: Union[int, str], name: str) -> Dict[str, Any]:
        """
        创建群文件文件夹
        
        :param group_id: 群号
        :param name: 文件夹名
        :return: 操作结果
        """
        return await self._call_api("create_group_file_folder", group_id=group_id, name=name)
    
    async def delete_group_folder(self, group_id: Union[int, str], folder_id: str) -> Dict[str, Any]:
        """
        删除群文件文件夹
        
        :param group_id: 群号
        :param folder_id: 文件夹ID
        :return: 操作结果
        """
        return await self._call_api("delete_group_folder", group_id=group_id, folder_id=folder_id)
    
    async def get_group_file_system_info(self, group_id: Union[int, str]) -> Dict[str, Any]:
        """
        获取群文件系统信息
        
        :param group_id: 群号
        :return: 文件系统信息
        """
        return await self._call_api("get_group_file_system_info", group_id=group_id)
    
    async def get_group_root_files(self, group_id: Union[int, str]) -> Dict[str, Any]:
        """
        获取群根目录文件列表
        
        :param group_id: 群号
        :return: 文件列表
        """
        return await self._call_api("get_group_root_files", group_id=group_id)
    
    async def get_group_files_by_folder(self, group_id: Union[int, str], folder_id: str) -> Dict[str, Any]:
        """
        获取群子目录文件列表
        
        :param group_id: 群号
        :param folder_id: 文件夹ID
        :return: 文件列表
        """
        return await self._call_api("get_group_files_by_folder", group_id=group_id, folder_id=folder_id)
    
    async def get_group_file_url(self, group_id: Union[int, str], file_id: str, busid: int) -> Dict[str, Any]:
        """
        获取群文件资源链接
        
        :param group_id: 群号
        :param file_id: 文件ID
        :param busid: 文件类型
        :return: 文件链接
        """
        return await self._call_api("get_group_file_url", group_id=group_id, file_id=file_id, busid=busid)
    
    async def get_private_file_url(self, user_id: Union[int, str], file_id: str) -> Dict[str, Any]:
        """
        获取私聊文件资源链接
        
        :param user_id: QQ号
        :param file_id: 文件ID
        :return: 文件链接
        """
        return await self._call_api("get_private_file_url", user_id=user_id, file_id=file_id)
    
    # ==================== 其他API ====================
    
    async def get_cookies(self, domain: str = "") -> Dict[str, Any]:
        """
        获取Cookies
        
        :param domain: 域名
        :return: Cookies
        """
        return await self._call_api("get_cookies", domain=domain)
    
    async def get_csrf_token(self) -> Dict[str, Any]:
        """
        获取CSRF Token
        
        :return: CSRF Token
        """
        return await self._call_api("get_csrf_token")
    
    async def get_credentials(self, domain: str = "") -> Dict[str, Any]:
        """
        获取QQ相关接口凭证
        
        :param domain: 域名
        :return: 凭证信息
        """
        return await self._call_api("get_credentials", domain=domain)
    
    async def get_version_info(self) -> Dict[str, Any]:
        """
        获取版本信息
        
        :return: 版本信息
        """
        return await self._call_api("get_version_info")