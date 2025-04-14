import os
from pathlib import Path
from aivk.api import AivkIO
import logging

logger = logging.getLogger("aivk.qq.base.utils")

def setup_napcat():
    """
    设置 napcat 相关配置
    """
    # 设置 napcat 的配置文件路径
    aivk_qq_config = AivkIO.get_config("qq")
    bot_uid = aivk_qq_config.get("bot_uid", None)
    root = aivk_qq_config.get("root", None)
    
    qq_data_dir : Path = AivkIO.get_aivk_root() / "data" / "qq" 
    logger.info(f"QQ 数据目录: {qq_data_dir}")
    
    napcat_logs : Path = qq_data_dir / "logs"
    napcat_data_dir : Path = qq_data_dir / "napcat"
    
    napcat_logs.mkdir(parents=True, exist_ok=True)
    os.environ["LOG_FILE_PATH"] = str(napcat_logs)

    import ncatbot.utils 
    import ncatbot.utils.assets.literals

    ncatbot.utils.WINDOWS_NAPCAT_DIR = str(napcat_data_dir)
    ncatbot.utils.assets.literals.WINDOWS_NAPCAT_DIR = str(napcat_data_dir)
    
    from ncatbot.adapter.nc.install import get_napcat_dir
    napcat_dir = get_napcat_dir()
    logger.info(f"napcat 安装目录: {napcat_dir}")

    from ncatbot.utils import config
    config.set_bot_uin(bot_uid)  # 设置 bot qq 号 (必填)
    config.set_root(root)  # 设置 bot 超级管理员账号 (建议填写)
    
    logger.info(f"设置 napcat 日志目录: {napcat_logs}")
    
    from ncatbot.core import BotClient 
    bot = BotClient()
    return bot