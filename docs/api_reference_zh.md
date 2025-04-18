# AIVK-QQ API 参考文档

## 消息相关接口

### 发送私聊消息
```python
from aivk_qq.napcat.api.actions import ActionType

async def send_private_message(user_id: int, message: str):
    """
    :param user_id: 接收用户QQ号
    :param message: 消息内容（支持CQ码）
    :return: 消息ID
    """
    return await client.execute(
        action=ActionType.SEND_PRIVATE_MSG,
        params={"user_id": user_id, "message": message}
    )
```

### 发送群组消息
```python
async def send_group_message(group_id: int, message: str):
    """
    :param group_id: 群号
    :param message: 消息内容（支持CQ码）
    :return: 消息ID
    """
    return await client.execute(
        action=ActionType.SEND_GROUP_MSG,
        params={"group_id": group_id, "message": message}
    )
```

## 群组管理接口

### 设置群成员禁言
```python
async def set_group_ban(group_id: int, user_id: int, duration: int = 600):
    """
    :param group_id: 群号
    :param user_id: 目标用户QQ号
    :param duration: 禁言时长（秒），默认600秒
    """
    return await client.execute(
        action=ActionType.SET_GROUP_BAN,
        params={
            "group_id": group_id,
            "user_id": user_id,
            "duration": duration
        }
    )
```

## 信息获取接口

### 获取登录信息
```python
async def get_login_info():
    """获取当前登录QQ号信息"""
    return await client.execute(ActionType.GET_LOGIN_INFO)
```

## 完整动作列表

| 动作类型 | 功能描述 | 参数示例 |
|---------|---------|---------|
| SEND_PRIVATE_MSG | 发送私聊消息 | `{"user_id": 123456, "message": "你好"}` |
| GET_GROUP_MEMBER_INFO | 获取群成员信息 | `{"group_id": 123456, "user_id": 789012}` |
| OCR_IMAGE | 图片OCR识别 | `{"image": "base64编码图片数据"}` |

## 类型安全验证示例
```python
from aivk_qq.napcat.api.actions import ActionType

def validate_action(action: str):
    if not ActionType.is_valid(action):
        raise ValueError(f"无效的API动作: {action}")
    return ActionType.from_string(action)
