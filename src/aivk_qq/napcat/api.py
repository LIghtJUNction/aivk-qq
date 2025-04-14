from pathlib import Path
from pydantic_core import Url
import requests
import logging
import zipfile
import os
import shutil
import json
from tqdm import tqdm

logger = logging.getLogger("aivk.qq.napcat.api")

class NapcatAPI:
    """
    Napcat API class for handling interactions with the Napcat service.
    """
    def __init__(self , napcat_root: Path = None , websocket: str = None , websocket_port: int = None , root: str = None , bot_uid: str = None):
        """
        Initialize the NapcatAPI instance.  
    
        :param napcat_root: Path to the napcat root directory
        :param websocket: WebSocket address
        :param websocket_port: WebSocket port
        """
        self.napcat_root = napcat_root
        self.websocket = websocket
        self.websocket_port = websocket_port
        self.root = root
        self.bot_uid = bot_uid
        self.github = "https://github.com/NapNeko/NapCatQQ"
        self.package_json ="https://raw.githubusercontent.com/NapNeko/NapCatQQ/main/package.json"
        self.github_proxy = "https://ghfast.top/"
        
        
    # ---------------------
    # region 基本方法
    # ---------------------

    def set_proxy(self, proxy: str):
        """
        Set the proxy for requests.
        """
        self.proxy = proxy

    @property
    def package_json_proxy(self) -> dict:
        """
        Get the package.json file from the Napcat GitHub repository.
        """
        return f"{self.github_proxy}{self.package_json}"
    
    @property
    def package_json_proxy_content(self) -> dict:
        """
        Get the content of the package.json file from the Napcat GitHub repository.
        """
        response = requests.get(self.package_json_proxy)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to fetch package.json")
        

    @property
    def package_json_content(self) -> dict:
        """
        Get the content of the package.json file from the Napcat GitHub repository.
        """
        response = requests.get(self.package_json)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to fetch package.json")

    @property
    def napcat_version_from_github(self) -> str:
        """
        Get the version of the Napcat service.
        """
        dotVersion = self.napcat_root / ".version"
        try:
            package_json = self.package_json_content
            version = package_json.get("version")
            if version:
                
                dotVersion.write_text(version)
                
                logger.info(f"获取到的版本号: {version}")
                return version
            else:
                logger.info(f"使用代理：{self.github_proxy}")
                package_json = self.package_json_proxy_content
                version = package_json.get("version")
                if version:

                    dotVersion.write_text(version)

                    logger.info(f"获取到的版本号: {version}")
                    return version
                else:
                    raise Exception("Version not found in package.json")
        except Exception as e:
            logger.error(f"试试使用 self.set_proxy({self.github_proxy}) 来使用其他代理地址")
            raise Exception(f"Error fetching version: {e}")
        
    
    @property
    def napcat_shell_download_url(self) -> str:
        """
        Get the download URL for the Napcat shell.
        """
        # https://github.com/NapNeko/NapCatQQ/releases/download/v4.7.19/NapCat.Shell.zip
        version = self.napcat_version_from_github
        if not version:
            raise Exception("Napcat version is not available.")
        download_url = f"{self.github_proxy}{self.github}/releases/download/v{version}/NapCat.Shell.zip"
        logger.info(f"下载地址: {download_url}")
        return download_url

    @property
    def need_update(self) -> bool:
        """
        Check if the Napcat shell needs to be updated.
        """
        dotVersion = self.napcat_root / ".version"
        if not dotVersion.exists():
            logger.info("没有找到版本文件，可能需要更新")
            return True
        else:
            current_version = dotVersion.read_text()
            new_version = self.napcat_version_from_github
            if current_version != new_version:
                logger.info(f"当前版本: {current_version}，新版本: {new_version}，需要更新")
                return True
            else:
                logger.info("当前版本已是最新，无需更新")
                return False

            
    
    # ---------------------
    # region 功能函数
    # ---------------------

    # 下载napcat shell -> self.napcat_root / "napcat"
    def download_for_win(self , force: bool = False) -> bool:
        """
        下载Napcat shell并解压到指定目录
        """
        logger.info("开始下载napcat shell...")
        target_dir = self.napcat_root / "napcat"
        download_url = self.napcat_shell_download_url
        temp_zip_path = self.napcat_root / "napcat_shell_temp.zip"

        # 创建目标目录
        os.makedirs(target_dir, exist_ok=True)

        try:
            # 下载压缩包
            logger.info(f"从 {download_url} 下载文件")
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # 获取文件大小用于进度条
            total_size = int(response.headers.get('content-length', 0))
            
            # 使用进度条下载文件
            with open(temp_zip_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc="下载进度") as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            logger.info(f"下载完成，文件保存在 {temp_zip_path}")
            
            # 清空目标目录
            if target_dir.exists() and force:
                logger.info(f"清空目标目录 {target_dir}")
                for item in os.listdir(target_dir):
                    item_path = target_dir / item
                    if item_path.is_file():
                        os.remove(item_path)
                    elif item_path.is_dir():
                        shutil.rmtree(item_path)
            
            # 解压文件
            logger.info(f"解压文件到 {target_dir}")
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
            
            logger.info("解压完成")
            
            # 删除临时文件
            os.remove(temp_zip_path)
            logger.info(f"已删除临时文件 {temp_zip_path}")
            
            logger.info(f"Napcat Shell 已成功安装到 {target_dir}")
            return True
        
        except Exception as e:
            logger.error(f"下载或解压过程中出现错误: {str(e)}")
            if temp_zip_path.exists():
                os.remove(temp_zip_path)
                logger.info(f"已删除临时文件 {temp_zip_path}")
            raise Exception(f"下载或解压Napcat Shell失败: {str(e)}")
        
    def download_for_linux(self):
        """
        linux ? 
        you can do it by yourself
        """
        logger.info(f" you can do it by yourself , please download it and put it in the {self.napcat_root}/napcat")

    def save_to_json(self):
        """
        将NapcatAPI实例序列化为JSON并保存到napcat_root/Napcat.json文件
        
        :return: 保存的文件路径
        :rtype: Path
        """
        if not self.napcat_root:
            raise ValueError("napcat_root未设置，无法保存配置")
            
        # 确保目录存在
        os.makedirs(self.napcat_root, exist_ok=True)
        
        # 准备序列化数据
        data = {
            "napcat_root": str(self.napcat_root) if self.napcat_root else None,
            "websocket": self.websocket,
            "websocket_port": self.websocket_port,
            "root": self.root,
            "bot_uid": self.bot_uid,
            "github": self.github,
            "package_json": self.package_json,
            "github_proxy": self.github_proxy
        }
        
        # 如果存在proxy属性则保存
        if hasattr(self, 'proxy'):
            data["proxy"] = self.proxy
            
        json_path = self.napcat_root / "Napcat.json"
        
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"NapcatAPI配置已保存到 {json_path}")
            return json_path
        except Exception as e:
            logger.error(f"保存NapcatAPI配置失败: {str(e)}")
            raise Exception(f"保存配置文件失败: {str(e)}")
    
    @classmethod
    def load_from_json(cls, napcat_root: Path = None):
        """
        从napcat_root/Napcat.json文件加载并反序列化为NapcatAPI实例
        
        :param napcat_root: Napcat根目录路径，如果未提供，将尝试从JSON文件中读取
        :type napcat_root: Path, optional
        :return: 加载的NapcatAPI实例
        :rtype: NapcatAPI
        """
        if napcat_root is None:
            raise ValueError("需要提供napcat_root参数来定位配置文件")
            
        json_path = napcat_root / "Napcat.json"
        
        if not json_path.exists():
            logger.warning(f"配置文件 {json_path} 不存在，将创建新实例")
            return cls(napcat_root=napcat_root)
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 创建实例时处理Path类型
            if "napcat_root" in data and data["napcat_root"]:
                data["napcat_root"] = Path(data["napcat_root"])
            else:
                # 如果JSON中没有napcat_root，使用传入的参数
                data["napcat_root"] = napcat_root
                
            # 创建NapcatAPI实例
            instance = cls(
                napcat_root=data.get("napcat_root"),
                websocket=data.get("websocket"),
                websocket_port=data.get("websocket_port"),
                root=data.get("root"),
                bot_uid=data.get("bot_uid")
            )
            
            # 设置其他属性
            if "github" in data:
                instance.github = data["github"]
            if "package_json" in data:
                instance.package_json = data["package_json"]
            if "github_proxy" in data:
                instance.github_proxy = data["github_proxy"]
            if "proxy" in data:
                instance.set_proxy(data["proxy"])
                
            logger.info(f"从 {json_path} 成功加载了NapcatAPI配置")
            return instance
        except Exception as e:
            logger.error(f"加载NapcatAPI配置失败: {str(e)}")
            logger.info("创建新的NapcatAPI实例")
            return cls(napcat_root=napcat_root)

    # ---------------------
    # region API 接口
    # ---------------------

