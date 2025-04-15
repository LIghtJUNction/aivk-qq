from enum import Enum, IntEnum


class PostType(str, Enum):
    """消息上报类型"""
    MESSAGE = "message"       # 消息事件
    MESSAGE_SENT = "message_sent"  # 消息发送事件
    NOTICE = "notice"         # 通知事件
    REQUEST = "request"       # 请求事件
    META_EVENT = "meta_event" # 元事件


class MessageType(str, Enum):
    """消息类型"""
    PRIVATE = "private"  # 私聊消息
    GROUP = "group"      # 群聊消息


class PrivateMessageSubType(str, Enum):
    """私聊消息子类型"""
    FRIEND = "friend"        # 好友私聊
    GROUP = "group"          # 群临时会话
    GROUP_SELF = "group_self"  # 群中自身发送
    OTHER = "other"          # 其他


class GroupMessageSubType(str, Enum):
    """群聊消息子类型"""
    NORMAL = "normal"  # 普通消息
    NOTICE = "notice"  # 系统提示


class MetaEventType(str, Enum):
    """元事件类型"""
    LIFECYCLE = "lifecycle"  # 生命周期事件
    HEARTBEAT = "heartbeat"  # 心跳事件


class NoticeType(str, Enum):
    """通知类型"""
    GROUP_UPLOAD = "group_upload"           # 群文件上传
    GROUP_ADMIN = "group_admin"             # 群管理员变更
    GROUP_DECREASE = "group_decrease"       # 群成员减少
    GROUP_INCREASE = "group_increase"       # 群成员增加
    GROUP_BAN = "group_ban"                 # 群禁言
    FRIEND_ADD = "friend_add"               # 好友添加
    GROUP_RECALL = "group_recall"           # 群消息撤回
    FRIEND_RECALL = "friend_recall"         # 好友消息撤回
    NOTIFY = "notify"                       # 通知事件
    GROUP_CARD = "group_card"               # 群名片变更
    OFFLINE_FILE = "offline_file"           # 接收到离线文件
    CLIENT_STATUS = "client_status"         # 客户端状态变更
    ESSENCE = "essence"                     # 精华消息变更
    GROUP_MSG_EMOJI_LIKE = "group_msg_emoji_like"  # 群聊表情回应


class NotifySubType(str, Enum):
    """通知子类型"""
    POKE = "poke"                 # 戳一戳
    INPUT_STATUS = "input_status"  # 输入状态更新
    TITLE = "title"               # 群成员头衔变更
    PROFILE_LIKE = "profile_like"  # 点赞


class GroupAdminSubType(str, Enum):
    """群管理员变动子类型"""
    SET = "set"        # 设置管理员
    UNSET = "unset"    # 取消管理员


class EssenceSubType(str, Enum):
    """精华消息子类型"""
    ADD = "add"        # 添加精华消息


class RequestType(str, Enum):
    """请求类型"""
    FRIEND = "friend"  # 好友请求
    GROUP = "group"    # 群请求


class SubType(str, Enum):
    """子类型"""
    # 好友请求子类型
    FRIEND_ADD = "add"  # 加好友请求
    
    # 群请求子类型
    GROUP_ADD = "add"     # 加群请求
    GROUP_INVITE = "invite"  # 邀请入群请求
    
    # 生命周期子类型
    CONNECT = "connect"    # 连接成功
    ENABLE = "enable"      # 启用
    DISABLE = "disable"    # 禁用
    
    # 群成员减少子类型
    LEAVE = "leave"    # 主动退群
    KICK = "kick"      # 被踢出群
    KICK_ME = "kick_me"  # 机器人被踢
    
    # 群成员增加子类型
    APPROVE = "approve"  # 管理员同意
    INVITE = "invite"    # 邀请入群
    
    # 群禁言子类型
    BAN = "ban"      # 禁言
    LIFT_BAN = "lift_ban"  # 解除禁言
    
    # 群管理员变动子类型
    SET = "set"      # 设置管理员
    UNSET = "unset"  # 取消管理员
    
    # 精华消息变更子类型
    ADD = "add"      # 添加
    DELETE = "delete"  # 删除
    
    # 通知事件子类型
    POKE = "poke"              # 戳一戳
    LUCKY_KING = "lucky_king"  # 红包运气王
    HONOR = "honor"            # 群荣誉变更
    INPUT_STATUS = "input_status"  # 输入状态更新
    TITLE = "title"            # 群成员头衔变更
    PROFILE_LIKE = "profile_like"  # 点赞
    
    # 消息子类型
    PRIVATE_FRIEND = "friend"         # 私聊消息 - 好友
    PRIVATE_GROUP = "group"           # 私聊消息 - 群临时
    PRIVATE_GROUP_SELF = "group_self" # 私聊消息 - 群中自身发送
    PRIVATE_OTHER = "other"           # 私聊消息 - 其他
    GROUP_NORMAL = "normal"           # 群聊消息 - 普通
    GROUP_NOTICE = "notice"           # 群聊消息 - 系统提示


class ActionType(str, Enum):
    """API动作类型"""
    # 标准 API
    SEND_PRIVATE_MSG = "send_private_msg"    # 发送私聊消息
    SEND_GROUP_MSG = "send_group_msg"        # 发送群消息
    SEND_MSG = "send_msg"                    # 发送消息
    DELETE_MSG = "delete_msg"                # 撤回消息
    GET_MSG = "get_msg"                      # 获取消息
    GET_FORWARD_MSG = "get_forward_msg"      # 获取合并转发消息
    SEND_LIKE = "send_like"                  # 发送好友赞
    SET_GROUP_KICK = "set_group_kick"        # 群组踢人
    SET_GROUP_BAN = "set_group_ban"          # 群组单人禁言
    SET_GROUP_WHOLE_BAN = "set_group_whole_ban"  # 群组全员禁言
    SET_GROUP_ADMIN = "set_group_admin"      # 设置群管理员
    SET_GROUP_CARD = "set_group_card"        # 设置群名片
    SET_GROUP_NAME = "set_group_name"        # 设置群名
    SET_GROUP_LEAVE = "set_group_leave"      # 退出群组
    SET_GROUP_SPECIAL_TITLE = "set_group_special_title"  # 设置群特殊头衔
    SET_FRIEND_ADD_REQUEST = "set_friend_add_request"    # 处理加好友请求
    SET_GROUP_ADD_REQUEST = "set_group_add_request"      # 处理加群请求
    GET_LOGIN_INFO = "get_login_info"        # 获取登录号信息
    GET_STRANGER_INFO = "get_stranger_info"  # 获取陌生人信息
    GET_FRIEND_LIST = "get_friend_list"      # 获取好友列表
    GET_GROUP_INFO = "get_group_info"        # 获取群信息
    GET_GROUP_LIST = "get_group_list"        # 获取群列表
    GET_GROUP_MEMBER_INFO = "get_group_member_info"  # 获取群成员信息
    GET_GROUP_MEMBER_LIST = "get_group_member_list"  # 获取群成员列表
    GET_GROUP_HONOR_INFO = "get_group_honor_info"    # 获取群荣誉信息
    GET_COOKIES = "get_cookies"              # 获取Cookies
    GET_CSRF_TOKEN = "get_csrf_token"        # 获取CSRF Token
    GET_CREDENTIALS = "get_credentials"      # 获取QQ相关接口凭证
    GET_RECORD = "get_record"                # 获取语音
    GET_IMAGE = "get_image"                  # 获取图片
    CAN_SEND_IMAGE = "can_send_image"        # 检查是否可以发送图片
    CAN_SEND_RECORD = "can_send_record"      # 检查是否可以发送语音
    GET_STATUS = "get_status"                # 获取运行状态
    GET_VERSION_INFO = "get_version_info"    # 获取版本信息
    CLEAN_CACHE = "clean_cache"              # 清理缓存
    
    # go-cqhttp 扩展 API
    SET_QQ_PROFILE = "set_qq_profile"                  # 设置登录号资料
    GET_MODEL_SHOW = "_get_model_show"                 # 获取在线机型
    SET_MODEL_SHOW = "_set_model_show"                 # 设置在线机型
    GET_ONLINE_CLIENTS = "get_online_clients"          # 获取当前账号在线客户端列表
    DELETE_FRIEND = "delete_friend"                    # 删除好友
    MARK_MSG_AS_READ = "mark_msg_as_read"              # 标记消息已读
    SEND_GROUP_FORWARD_MSG = "send_group_forward_msg"  # 发送合并转发(群聊)
    SEND_PRIVATE_FORWARD_MSG = "send_private_forward_msg"  # 发送合并转发(好友)
    GET_GROUP_MSG_HISTORY = "get_group_msg_history"    # 获取群消息历史记录
    OCR_IMAGE = "ocr_image"                            # 图片OCR
    GET_GROUP_SYSTEM_MSG = "get_group_system_msg"      # 获取群系统消息
    GET_ESSENCE_MSG_LIST = "get_essence_msg_list"      # 获取精华消息列表
    GET_GROUP_AT_ALL_REMAIN = "get_group_at_all_remain"  # 获取群@全体成员剩余次数
    SET_GROUP_PORTRAIT = "set_group_portrait"          # 设置群头像
    SET_ESSENCE_MSG = "set_essence_msg"                # 设置精华消息
    DELETE_ESSENCE_MSG = "delete_essence_msg"          # 移出精华消息
    SEND_GROUP_SIGN = "send_group_sign"                # 群打卡
    SEND_GROUP_NOTICE = "_send_group_notice"           # 发送群公告
    GET_GROUP_NOTICE = "_get_group_notice"             # 获取群公告
    UPLOAD_GROUP_FILE = "upload_group_file"            # 上传群文件
    DELETE_GROUP_FILE = "delete_group_file"            # 删除群文件
    CREATE_GROUP_FILE_FOLDER = "create_group_file_folder"  # 创建群文件文件夹
    DELETE_GROUP_FOLDER = "delete_group_folder"        # 删除群文件文件夹
    GET_GROUP_FILE_SYSTEM_INFO = "get_group_file_system_info"  # 获取群文件系统信息
    GET_GROUP_ROOT_FILES = "get_group_root_files"      # 获取群根目录文件列表
    GET_GROUP_FILES_BY_FOLDER = "get_group_files_by_folder"  # 获取群子目录文件列表
    GET_GROUP_FILE_URL = "get_group_file_url"          # 获取群文件资源链接
    UPLOAD_PRIVATE_FILE = "upload_private_file"        # 上传私聊文件
    DOWNLOAD_FILE = "download_file"                    # 下载文件到缓存目录
    CHECK_URL_SAFELY = "check_url_safely"              # 检查链接安全性
    HANDLE_QUICK_OPERATION = ".handle_quick_operation"  # 对事件执行快速操作
    
    # napcat 扩展 API
    SET_GROUP_SIGN_NAPCAT = "set_group_sign"            # 群签到
    ARK_SHARE_PEER = "ArkSharePeer"                     # 推荐联系人/群聊
    ARK_SHARE_GROUP = "ArkShareGroup"                   # 推荐群聊
    GET_ROBOT_UIN_RANGE = "get_robot_uin_range"         # 获取机器人QQ号区间
    SET_ONLINE_STATUS = "set_online_status"             # 设置在线状态
    GET_FRIENDS_WITH_CATEGORY = "get_friends_with_category"  # 获取好友分类列表
    SET_QQ_AVATAR = "set_qq_avatar"                     # 设置头像
    GET_FILE = "get_file"                               # 获取文件信息
    FORWARD_FRIEND_SINGLE_MSG = "forward_friend_single_msg"  # 转发单条信息到私聊
    FORWARD_GROUP_SINGLE_MSG = "forward_group_single_msg"  # 转发单条信息到群聊
    TRANSLATE_EN2ZH = "translate_en2zh"                 # 英译中翻译
    SET_MSG_EMOJI_LIKE = "set_msg_emoji_like"           # 设置消息的表情回复
    SEND_FORWARD_MSG = "send_forward_msg"               # 发送合并转发
    MARK_PRIVATE_MSG_AS_READ = "mark_private_msg_as_read"  # 标记私聊信息已读
    MARK_GROUP_MSG_AS_READ = "mark_group_msg_as_read"   # 标记群聊信息已读
    GET_FRIEND_MSG_HISTORY = "get_friend_msg_history"   # 获取私聊记录
    CREATE_COLLECTION = "create_collection"             # 创建文本收藏
    GET_COLLECTION_LIST = "get_collection_list"         # 获取收藏列表
    SET_SELF_LONGNICK = "set_self_longnick"             # 设置个人签名
    GET_RECENT_CONTACT = "get_recent_contact"           # 获取最近的聊天记录
    MARK_ALL_AS_READ = "_mark_all_as_read"              # 标记所有为已读
    GET_PROFILE_LIKE = "get_profile_like"               # 获取自身点赞列表
    FETCH_CUSTOM_FACE = "fetch_custom_face"             # 获取收藏表情
    FETCH_EMOJI_LIKE = "fetch_emoji_like"               # 拉取表情回应列表
    SET_INPUT_STATUS = "set_input_status"               # 设置输入状态
    GET_GROUP_INFO_EX = "get_group_info_ex"             # 获取群组额外信息
    GET_GROUP_IGNORE_ADD_REQUEST = "get_group_ignore_add_request"  # 获取群组忽略的通知
    DEL_GROUP_NOTICE = "_del_group_notice"              # 删除群聊公告
    GET_PROFILE_LIKE_2 = "get_profile_like"             # 获取用户点赞信息
    FRIEND_POKE = "friend_poke"                         # 私聊戳一戳
    GROUP_POKE = "group_poke"                           # 群聊戳一戳
    NC_GET_PACKET_STATUS = "nc_get_packet_status"       # 获取PacketServer状态
    NC_GET_USER_STATUS = "nc_get_user_status"           # 获取陌生人在线状态
    NC_GET_RKEY = "nc_get_rkey"                         # 获取Rkey
    GET_GROUP_SHUT_LIST = "get_group_shut_list"         # 获取群聊被禁言用户
    GET_MINI_APP_ARK = "get_mini_app_ark"               # 签名小程序卡片
    GET_AI_RECORD = "get_ai_record"                     # AI文字转语音
    GET_AI_CHARACTERS = "get_ai_characters"             # 获取AI语音角色列表
    SEND_GROUP_AI_RECORD = "send_group_ai_record"       # 群聊发送AI语音
    SEND_POKE = "send_poke"                             # 群聊/私聊戳一戳


class MessageSegmentType(str, Enum):
    """消息段类型"""
    TEXT = "text"                # 纯文本
    FACE = "face"                # QQ表情
    IMAGE = "image"              # 图片
    RECORD = "record"            # 语音
    VIDEO = "video"              # 短视频
    AT = "at"                    # @某人
    RPS = "rps"                  # 猜拳魔法表情
    DICE = "dice"                # 掷骰子魔法表情
    SHAKE = "shake"              # 窗口抖动(戳一戳)
    POKE = "poke"                # 戳一戳
    ANONYMOUS = "anonymous"      # 匿名发消息
    SHARE = "share"              # 链接分享
    CONTACT = "contact"          # 推荐好友/群
    LOCATION = "location"        # 位置
    MUSIC = "music"              # 音乐分享
    REPLY = "reply"              # 回复
    FORWARD = "forward"          # 合并转发
    NODE = "node"                # 合并转发节点
    XML = "xml"                  # XML消息
    JSON = "json"                # JSON消息
    CARD_IMAGE = "cardimage"     # 卡片图片
    TTS = "tts"                  # 文本转语音
    FILE = "file"                # 文件
    AT_ALL = "at_all"            # @全体成员


class OnlineStatus(int, Enum):
    """在线状态"""
    ONLINE = 11      # 在线
    OFFLINE = 21     # 离线
    AWAY = 31        # 离开
    INVISIBLE = 41   # 隐身
    BUSY = 50        # 忙碌
    Q_ME = 60        # Q我吧
    DO_NOT_DISTURB = 70  # 请勿打扰


class HonorType(str, Enum):
    """群荣誉类型"""
    TALKATIVE = "talkative"        # 龙王
    PERFORMER = "performer"        # 群聊之火
    LEGEND = "legend"              # 群聊炽焰
    STRONG_NEWBIE = "strong_newbie"  # 冒尖小春笋
    EMOTION = "emotion"            # 快乐之源
    ALL = "all"                    # 所有类型


class GroupRole(str, Enum):
    """群成员角色"""
    OWNER = "owner"      # 群主
    ADMIN = "admin"      # 管理员
    MEMBER = "member"    # 普通成员


class UserStatus(IntEnum):
    """用户在线状态"""
    ONLINE = 10          # 在线
    Q_ME = 10            # Q我吧
    AWAY = 60            # 离开
    BUSY = 30            # 忙碌
    DO_NOT_DISTURB = 50  # 请勿打扰
    INVISIBLE = 70       # 隐身
    LISTENING = 40       # 听歌中


class UserExtStatus(IntEnum):
    """用户扩展状态"""
    NONE = 0               # 无扩展状态
    SPRING_LIMITED = 1028  # 春日限定
    DREAM_TOGETHER = 2037  # 一起元梦
    STAR_PARTNER = 2025    # 求星搭子
    EMPTIED = 2026         # 被掏空
    WEATHER_TODAY = 2014   # 今日天气
    CRASHED = 1030         # 我crash了
    LOVE_YOU = 2019        # 爱你
    IN_LOVE = 2006         # 恋爱中
    LUCKY_KOI = 1051       # 好运锦鲤
    MERCURY_RETROGRADE = 1071  # 水逆退散
    HIGH_SPIRITS = 1201    # 嗨到飞起
    ENERGETIC = 1056       # 元气满满
    BABY_CERTIFIED = 1058  # 宝宝认证
    SPEECHLESS = 1070      # 一言难尽
    MUDDLEHEADED = 1063    # 难得糊涂
    EMO = 2001             # emo中
    TOO_DIFFICULT = 1401   # 我太难了
    FIGURED_OUT = 1062     # 我想开了
    IM_FINE = 2013         # 我没事
    WANT_QUIET = 1052      # 想静静
    RELAXED = 1061         # 悠哉哉
    TRAVELING = 1059       # 去旅行
    WEAK_SIGNAL = 2015     # 信号弱
    OUT_PLAYING = 1011     # 出去浪
    DOING_HOMEWORK = 2003  # 肝作业
    STUDYING = 2012        # 学习中
    WORKING = 1018         # 搬砖中
    SLACKING = 2023        # 摸鱼中
    BORED = 1300           # 无聊中
    GAMING = 1060          # timi中
    SLEEPING = 1027        # 睡觉中
    STAYING_UP = 1016      # 熬夜中
    WATCHING_DRAMA = 1032  # 追剧中
    FEELING_COLD = 1021    # 有亿点冷
    HELLO_MONTH = 2050     # 一月你好
    MY_BATTERY = 2053      # 我的电量
    DEFAULT = 1000         # 默认扩展状态


class BatteryStatus(IntEnum):
    """电池状态"""
    NONE = 0  # 无电池状态信息
    # 可以根据需要添加其他电池状态值


class CompatibilityStatus(str, Enum):
    """事件兼容性状态"""
    AVAILABLE = "✅"      # 可用
    UNAVAILABLE = "❌"    # 不可用
    PARTIAL = "⏹"       # 部分可用


class EventCompatibility(Enum):
    """事件兼容性信息"""
    # Meta事件
    META_EVENT_LIFECYCLE = ("meta_event.lifecycle", "生命周期", CompatibilityStatus.AVAILABLE, "")
    META_EVENT_LIFECYCLE_ENABLE = ("meta_event.lifecycle.enable", "生命周期 - OneBot 启用", CompatibilityStatus.UNAVAILABLE, "")
    META_EVENT_LIFECYCLE_DISABLE = ("meta_event.lifecycle.disable", "生命周期 - OneBot 停用", CompatibilityStatus.UNAVAILABLE, "")
    META_EVENT_LIFECYCLE_CONNECT = ("meta_event.lifecycle.connect", "生命周期 - WebSocket 连接成功", CompatibilityStatus.AVAILABLE, "")
    META_EVENT_HEARTBEAT = ("meta_event.heartbeat", "心跳", CompatibilityStatus.AVAILABLE, "")
    
    # 消息事件
    MESSAGE_PRIVATE = ("message.private", "私聊消息", CompatibilityStatus.AVAILABLE, "")
    MESSAGE_PRIVATE_FRIEND = ("message.private.friend", "私聊消息 - 好友", CompatibilityStatus.AVAILABLE, "")
    MESSAGE_PRIVATE_GROUP = ("message.private.group", "私聊消息 - 群临时", CompatibilityStatus.AVAILABLE, "")
    MESSAGE_PRIVATE_GROUP_SELF = ("message.private.group_self", "私聊消息 - 群中自身发送", CompatibilityStatus.UNAVAILABLE, "")
    MESSAGE_PRIVATE_OTHER = ("message.private.other", "私聊消息 - 其他", CompatibilityStatus.UNAVAILABLE, "")
    MESSAGE_GROUP = ("message.group", "群聊消息", CompatibilityStatus.AVAILABLE, "")
    MESSAGE_GROUP_NORMAL = ("message.group.normal", "群聊消息 - 普通", CompatibilityStatus.AVAILABLE, "")
    MESSAGE_GROUP_NOTICE = ("message.group.notice", "群聊消息 - 系统提示", CompatibilityStatus.UNAVAILABLE, "")
    
    # 消息发送事件
    MESSAGE_SENT_PRIVATE = ("message_sent.private", "私聊消息", CompatibilityStatus.AVAILABLE, "")
    MESSAGE_SENT_PRIVATE_FRIEND = ("message_sent.private.friend", "私聊消息 - 好友", CompatibilityStatus.AVAILABLE, "")
    MESSAGE_SENT_PRIVATE_GROUP = ("message_sent.private.group", "私聊消息 - 群临时", CompatibilityStatus.AVAILABLE, "")
    MESSAGE_SENT_PRIVATE_GROUP_SELF = ("message_sent.private.group_self", "私聊消息 - 群中自身发送", CompatibilityStatus.UNAVAILABLE, "")
    MESSAGE_SENT_PRIVATE_OTHER = ("message_sent.private.other", "私聊消息 - 其他", CompatibilityStatus.UNAVAILABLE, "")
    MESSAGE_SENT_GROUP = ("message_sent.group", "群聊消息", CompatibilityStatus.AVAILABLE, "")
    MESSAGE_SENT_GROUP_NORMAL = ("message_sent.group.normal", "群聊消息 - 普通", CompatibilityStatus.AVAILABLE, "")
    MESSAGE_SENT_GROUP_NOTICE = ("message_sent.group.notice", "群聊消息 - 系统提示", CompatibilityStatus.UNAVAILABLE, "")
    
    # 请求事件
    REQUEST_FRIEND = ("request.friend", "加好友请求", CompatibilityStatus.AVAILABLE, "")
    REQUEST_GROUP_ADD = ("request.group.add", "加群请求", CompatibilityStatus.AVAILABLE, "")
    REQUEST_GROUP_INVITE = ("request.group.invite", "邀请登录号入群", CompatibilityStatus.AVAILABLE, "")
    
    # 通知事件
    NOTICE_FRIEND_ADD = ("notice.friend_add", "好友添加", CompatibilityStatus.AVAILABLE, "")
    NOTICE_FRIEND_RECALL = ("notice.friend_recall", "私聊消息撤回", CompatibilityStatus.AVAILABLE, "")
    NOTICE_OFFLINE_FILE = ("notice.offline_file", "接收到离线文件", CompatibilityStatus.UNAVAILABLE, "")
    NOTICE_CLIENT_STATUS = ("notice.client_status", "其他客户端在线状态变更", CompatibilityStatus.UNAVAILABLE, "")
    NOTICE_GROUP_ADMIN = ("notice.group_admin", "群聊管理员变动", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_ADMIN_SET = ("notice.group_admin.set", "群聊管理员变动 - 增加", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_ADMIN_UNSET = ("notice.group_admin.unset", "群聊管理员变动 - 减少", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_BAN = ("notice.group_ban", "群聊禁言", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_BAN_BAN = ("notice.group_ban.ban", "群聊禁言 - 禁言", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_BAN_LIFT_BAN = ("notice.group_ban.lift_ban", "群聊禁言 - 取消禁言", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_CARD = ("notice.group_card", "群成员名片更新", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_DECREASE = ("notice.group_decrease", "群聊成员减少", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_DECREASE_LEAVE = ("notice.group_decrease.leave", "群聊成员减少 - 主动退群", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_DECREASE_KICK = ("notice.group_decrease.kick", "群聊成员减少 - 成员被踢", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_DECREASE_KICK_ME = ("notice.group_decrease.kick_me", "群聊成员减少 - 登录号被踢", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_INCREASE = ("notice.group_increase", "群聊成员增加", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_INCREASE_APPROVE = ("notice.group_increase.approve", "群聊成员增加 - 管理员已同意入群", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_INCREASE_INVITE = ("notice.group_increase.invite", "群聊成员增加 - 管理员邀请入群", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_RECALL = ("notice.group_recall", "群聊消息撤回", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_UPLOAD = ("notice.group_upload", "群聊文件上传", CompatibilityStatus.AVAILABLE, "")
    NOTICE_GROUP_MSG_EMOJI_LIKE = ("notice.group_msg_emoji_like", "群聊表情回应", CompatibilityStatus.PARTIAL, "仅收自己的 其余扩展接口拉取")
    NOTICE_ESSENCE = ("notice.essence", "群聊设精", CompatibilityStatus.AVAILABLE, "")
    NOTICE_ESSENCE_ADD = ("notice.essence.add", "群聊设精 - 增加", CompatibilityStatus.AVAILABLE, "")
    NOTICE_NOTIFY_POKE = ("notice.notify.poke", "戳一戳", CompatibilityStatus.AVAILABLE, "")
    NOTICE_NOTIFY_INPUT_STATUS = ("notice.notify.input_status", "输入状态更新", CompatibilityStatus.AVAILABLE, "")
    NOTICE_NOTIFY_TITLE = ("notice.notify.title", "群成员头衔变更", CompatibilityStatus.AVAILABLE, "")
    NOTICE_NOTIFY_PROFILE_LIKE = ("notice.notify.profile_like", "点赞", CompatibilityStatus.AVAILABLE, "")
    
    def __init__(self, event_name, description, status, remark):
        self.event_name = event_name
        self.description = description
        self.status = status
        self.remark = remark
    
    @classmethod
    def get_event_compatibility_map(cls):
        """获取事件兼容性映射表"""
        return {event.event_name: event for event in cls}
    
    @classmethod
    def is_available(cls, event_name):
        """检查事件是否可用"""
        event = cls.get_event_compatibility_map().get(event_name)
        return event is not None and event.status == CompatibilityStatus.AVAILABLE
    
    @classmethod
    def get_compatibility_info(cls, event_name):
        """获取事件兼容性信息"""
        return cls.get_event_compatibility_map().get(event_name)


# 使用示例:
# from aivk_qq.base.enums import PostType, MessageType, MessageSegmentType
# 
# def handle_message(message_data):
#     if message_data.get("post_type") == PostType.MESSAGE:
#         if message_data.get("message_type") == MessageType.PRIVATE:
#             print("收到私聊消息")
#         elif message_data.get("message_type") == MessageType.GROUP:
#             print("收到群消息")
#
# def create_at_message(user_id):
#     return [{
#         "type": MessageSegmentType.AT,
#         "data": {"qq": str(user_id)}
#     }]