from pathlib import Path
import time
from pydantic_core import Url
import requests
import logging
import zipfile
import os
import shutil
import json
from tqdm import tqdm
import asyncio
from websockets.asyncio.server import serve as ws_serve
from websockets.asyncio.client import connect as ws_connect
from websockets.exceptions import ConnectionClosedError

from aivk.api import AivkIO

logger = logging.getLogger("aivk.qq.napcat.api")


class NapcatAPI:
    """
    Napcat API class for handling interactions with the Napcat service.
    """
    def __init__(self , aivk_root: Path = None , websocket: str = None , websocket_port: int = None , root: str = None , bot_uid: str = None):
        """
        Initialize the NapcatAPI instance.  
    
        :param aivk_root: Path to the AIVK root directory
        :param websocket: WebSocket address
        :param websocket_port: WebSocket port
        """
        self.aivk_root = aivk_root
        self.websocket = websocket
        self.websocket_port = websocket_port
        self.websocket_path = "/aivk/qq"  # 默认路径 
        self.root = root
        self.bot_uid = bot_uid
        self.github = "https://github.com/NapNeko/NapCatQQ"
        self.package_json ="https://raw.githubusercontent.com/NapNeko/NapCatQQ/main/package.json"
        self.github_proxy = "https://ghfast.top/"
        self.ws_connection = None
        self.server = None


    # ---------------------
    # region 基本方法
    # ---------------------

    def set_proxy(self, proxy: str):
        """
        Set the proxy for requests.
        """
        self.proxy = proxy


    def set_websocket_path(self, path: str):
        """
        Set the WebSocket path.
        """
        self.websocket_path = path

    @property
    def napcat_root(self) -> Path:
        """
        Get the Napcat root directory.
        """
        if self.aivk_root:
            return self.aivk_root / "data" / "qq" / "napcat_root"
        else:
            raise ValueError("Napcat root directory not set")


    @property
    def uri(self) -> str:
        """
        Get the WebSocket URI.
        """
        if self.websocket and self.websocket_port:
            return f"ws://{self.websocket}:{self.websocket_port}{self.websocket_path}"
        else:
            raise ValueError("WebSocket address or port not set")


    @property
    def closed(self) -> bool:
        """
        Check if the WebSocket connection is closed.
        """
        return self.ws_connection is None
    
    async def close_ws(self):
        """
        关闭WebSocket连接
        """
        logger.info("关闭WebSocket连接")

        if self.ws_connection:
            await self.ws_connection.close()
        self.ws_connection = None
        
        if self.server:
            self.server.close()
            try:
                await self.server.wait_closed()
                logger.info("WebSocket服务器已关闭")
            except:
                pass
            self.server = None

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
        将NapcatAPI实例序列化为JSON并保存到aivk_root/data/qq/napcat_root/Napcat.json文件
        
        :return: 保存的文件路径
        :rtype: Path
        """
        if not self.aivk_root:
            raise ValueError("aivk_root未设置，无法保存配置")
            
        # 确保目录存在
        os.makedirs(self.napcat_root, exist_ok=True)
        
        # 准备序列化数据
        data = {
            "aivk_root": str(self.aivk_root) if self.aivk_root else None,
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
    def load_from_json(cls, aivk_root: Path = None):
        """
        从aivk_root/data/qq/napcat_root/Napcat.json文件加载并反序列化为NapcatAPI实例
        
        :param aivk_root: AIVK根目录路径，如果未提供，将尝试从JSON文件中读取
        :type aivk_root: Path, optional
        :return: 加载的NapcatAPI实例
        :rtype: NapcatAPI
        """
        if aivk_root is None:
            raise ValueError("需要提供aivk_root参数来定位配置文件")
        
        napcat_root = aivk_root / "data" / "qq" / "napcat_root"    
        json_path = napcat_root / "Napcat.json"
        
        if not json_path.exists():
            logger.warning(f"配置文件 {json_path} 不存在，将创建新实例")
            return cls(aivk_root=aivk_root)
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 创建实例时处理Path类型
            if "aivk_root" in data and data["aivk_root"]:
                data["aivk_root"] = Path(data["aivk_root"])
            elif "napcat_root" in data and data["napcat_root"]:
                # 向后兼容：如果有旧格式的napcat_root但没有aivk_root
                logger.warning("使用旧格式的配置文件，将napcat_root转换为aivk_root")
                # 这里假设aivk_root是napcat_root的父目录的父目录的父目录
                # 即 aivk_root/data/qq/napcat_root
                data["aivk_root"] = Path(data["napcat_root"]).parent.parent.parent
            else:
                # 如果JSON中没有aivk_root，使用传入的参数
                data["aivk_root"] = aivk_root
                
            # 创建NapcatAPI实例
            instance = cls(
                aivk_root=data.get("aivk_root"),
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
            return cls(aivk_root=aivk_root)

    # ---------------------
    # region API ws 链接准备
    # ---------------------


    """
        这里的正向 / 反向 是Napcat的 WebSocket 连接模式 

        正向：Napcat 主动 连接 aivk-qq
        反向：aivk-qq 主动连接 Napcat

        推荐：反向连接模式 ： Napcat 需手动配置 适合远程连接
        正向连接模式：Napcat 依旧需手动配置 适合本地连接
    
    """
    
    async def ws_server(self, host: str = "localhost", port: int = 10143) -> None:
        """
        启动WebSocket服务器（正向连接模式）
        
        :param host: 主机地址，默认为localhost
        :param port: 端口号，默认为10143
        :return: WebSocket连接对象
        """
        if self.ws_connection:
            logger.info("已存在WebSocket连接，将关闭旧连接")
            await self.close_ws()
        
        logger.info(f"启动WebSocket服务器，监听地址: ws://{host}:{port}")
        
        connected_event = asyncio.Event()
        
        async def handler(websocket):
            """
            处理WebSocket连接
            
            :param websocket: WebSocket连接对象
            """
            logger.info(f"客户端已连接: {websocket.remote_address}")
            self.ws_connection = websocket
            connected_event.set()
            await asyncio.Future()
        
        # 使用简单的方式启动WebSocket服务器
        self.server = await ws_serve(handler, host, port)
        
        # 等待客户端连接
        logger.info(f"等待客户端连接到 ws://{host}:{port}...")
        await connected_event.wait()
        logger.info("客户端已连接成功")
        
        return self.ws_connection
    
    async def ws_client(self, uri: str | None = None):
        """
        创建WebSocket客户端连接（反向连接模式）
        
        :param uri: WebSocket服务器地址，格式如: ws://localhost:10143
                   如果不提供，将使用实例化时的websocket和websocket_port构建地址
        :return: WebSocket连接对象
        """
        if self.ws_connection:
            logger.info("已存在WebSocket连接，将关闭旧连接")
            await self.close_ws()
        
        if uri is None:
            if not self.websocket or not self.websocket_port:
                raise ValueError("未提供WebSocket URI，且实例中websocket或websocket_port未设置")
        else:
            # 验证uri格式 提取 并覆盖3个参数 ： self.websocket , self.websocket_port , self.websocket_path
            # 如果提供了uri，则从中提取host和port
            # 例如：ws://localhost:10143/aivk/qq
            # ws://localhost:10143
            # ws://localhost:10143/aivk/qq
            try:
                parsed_url = Url(uri)
                self.websocket = parsed_url.host
                self.websocket_port = parsed_url.port
                self.websocket_path = parsed_url.path or "/"
            except Exception as e:
                logger.error(f"解析WebSocket URI失败: {str(e)}")
                raise ValueError(f"无效的WebSocket URI: {uri}")
            
            # 保存
            self.save_to_json()

        logger.info(f"尝试连接到WebSocket服务器: {self.uri}")
        try:
            # 使用正确的connect方法
            self.ws_connection = await ws_connect(self.uri)
            logger.info(f"已成功连接到WebSocket服务器: {self.uri}")
            return self.ws_connection
        except Exception as e:
            logger.error(f"连接WebSocket服务器失败: {str(e)}")
            raise Exception(f"连接WebSocket服务器失败: {str(e)}")



    # region CLI 测试

    @classmethod
    async def test_server_connection(cls, host: str = "127.0.0.1", port: int = 10143, timeout: float = 30.0) -> bool:
        """
        测试WebSocket服务器连接（正向连接模式）

        此方法启动一个临时WebSocket服务器，并等待指定时间看是否有客户端连接。
        适用于测试Napcat是否能主动连接到aivk-qq。

        :param host: 服务器主机地址，默认为127.0.0.1
        :param port: 服务器端口号，默认为10143
        :param timeout: 等待连接的超时时间（秒），默认为30秒
        :return: 连接测试结果，True表示成功，False表示失败
        """
        logger.info(f"测试WebSocket服务器连接，地址: ws://{host}:{port}，超时: {timeout}秒")

        # 创建临时NapcatAPI实例
        aivk_root = AivkIO.get_aivk_root()
        server_api = cls.load_from_json(aivk_root=aivk_root)
        if server_api.root is None or server_api.root == "" :
            logger.warning("请先使用aivk-qq config 命令配置好！")
            return False

        # 创建事件标记连接状态
        connected_event = asyncio.Event()
        message_received_event = asyncio.Event()

        # 定义服务器任务
        async def run_server():
            try:
                # 使用ws_server方法启动服务器
                ws_connection = await server_api.ws_server(host=host, port=port)
                logger.info("客户端已连接到服务器")
                connected_event.set()

                # 保持连接并监听消息，直到测试结束
                try:
                    logger.info("开始监听客户端消息...")
                    while True:
                        try:
                            message = await ws_connection.recv()
                            print(f"收到客户端消息: {message}")
                            print(f"消息类型: {type(message)}")
                            time.sleep(1)
                            try:
                                # 正确解析JSON字符串为字典
                                message_dict = json.loads(message)
                                
                                # 检查是否为消息类型，并且是否包含"exit"指令
                                if message_dict.get("post_type","") == "message":
                                    user_id = message_dict.get("user_id")
                                    raw_message = message_dict.get("raw_message", "")
                                    
                                    # 处理exit命令
                                    if user_id == int(server_api.root) and raw_message.strip().lower() == "exit":
                                        logger.info("收到exit命令，准备退出测试")
                                        print("\n收到exit命令，准备退出测试...")
                                        
                                        # 发送退出确认消息
                                        response = {
                                            "action": "send_private_msg",
                                            "params": {
                                                "user_id": user_id,
                                                "message": "好的，正在退出测试服务器...",
                                                "auto_escape": False,
                                            }
                                        }
                                        await ws_connection.send(json.dumps(response))
                                        
                                        # 设置消息接收事件并退出循环
                                        message_received_event.set()
                                        
                                        # 关闭WebSocket连接
                                        await server_api.close_ws()
                                        
                                        # 取消future使主程序退出
                                        server_task.cancel()
                                        return True
                                
                                message_received_event.set()  # 标记收到消息
                                
                                # 对于各种消息类型的响应处理
                                if message_dict.get("post_type") == "meta_event" and message_dict.get("meta_event_type") == "heartbeat":
                                    # 心跳事件不需要响应
                                    pass
                                elif message_dict.get("post_type") == "meta_event" and message_dict.get("meta_event_type") == "lifecycle":
                                    # 生命周期事件，发送欢迎消息
                                    response = {
                                        "action": "send_private_msg",
                                        "params": {
                                            "user_id": int(server_api.root),
                                            "message": "AIVK-QQ 连接测试服务器已启动\n发送 exit 可退出测试",
                                            "auto_escape": False,
                                        }
                                    }
                                    await ws_connection.send(json.dumps(response))
                                elif message_dict.get("post_type") == "message":
                                    # 是消息但不是exit命令，发送提示
                                    response = {
                                        "action": "send_private_msg",
                                        "params": {
                                            "user_id": message_dict.get("user_id"),
                                            "message": f"收到您的消息: {message_dict.get('raw_message', '')}\n发送 exit 可退出测试",
                                            "auto_escape": False,
                                        }
                                    }
                                    await ws_connection.send(json.dumps(response))
                                                                    
                            except json.JSONDecodeError as e:
                                logger.error(f"解析JSON消息失败: {e}")
                                print(f"无法解析消息为JSON: {e}")
                            except Exception as e:
                                logger.error(f"接收消息时出错: {e}")
                                print(f"处理消息时出错: {e}")
                        except ConnectionClosedError as e:
                            if (e.code == 1000):
                                logger.info("WebSocket连接正常关闭 (1000 OK)")
                            else:
                                logger.warning(f"WebSocket连接关闭: {e.code} {e.reason}")
                            break
                        except Exception as e:
                            logger.error(f"接收消息时出错: {e}")
                            break
                except asyncio.CancelledError:
                    logger.info("消息监听任务被取消")
            except Exception as e:
                if ("1000 (OK)" in str(e)):
                    logger.info("WebSocket连接正常关闭 (1000 OK)")
                    if not connected_event.is_set():
                        connected_event.set()
                else:
                    logger.error(f"服务器运行错误: {e}")
            finally:
                logger.info("服务器任务结束")

        # 启动服务器任务
        server_task = asyncio.create_task(run_server())

        # 等待连接或超时
        try:
            await asyncio.wait_for(connected_event.wait(), timeout=timeout)
            logger.info("测试成功：客户端已连接")

            # 连接成功后不立即退出，等待客户端消息或通知用户可以手动停止
            print("\n✅ 连接测试成功！")
            print("客户端已成功连接到服务器")
            print("\n==================================================")
            print("服务器将继续运行并监听消息...")
            print("按Ctrl+C手动停止测试")
            print("==================================================\n")

            # 这里是关键：持续运行直到程序被手动终止
            try:
                # 创建一个不会自动完成的future
                forever = asyncio.Future()
                await forever
            except asyncio.CancelledError:
                # 如果future被取消，则正常退出
                logger.info("测试被手动终止")

            # 告知调用者测试成功 - 但实际上这行代码不会被执行到，除非future被取消
            return True

        except asyncio.TimeoutError:
            logger.info(f"测试失败：等待客户端连接超时 ({timeout}秒)")
            return False

    @classmethod
    async def test_client_connection(cls, uri: str | None = None, timeout: float = 40) -> bool:
        """
        测试WebSocket客户端连接（反向连接模式）
        
        此方法尝试作为客户端连接到指定的WebSocket服务器。
        适用于测试aivk-qq是否能主动连接到Napcat。
        
        :param uri: WebSocket服务器地址，格式为ws://host:port/path，如果不提供则使用配置中的地址
        :param timeout: 连接超时时间（秒），默认为40秒
        :return: 连接测试结果，True表示成功，False表示失败
        """
        logger.info(f"测试WebSocket客户端连接，目标: {uri or '配置中的地址'}，超时: {timeout}秒")
        
        # 创建临时实例并加载配置
        aivk_root = AivkIO.get_aivk_root()
        client_api = cls(aivk_root=aivk_root)
        
        # 尝试加载配置，失败则使用默认值
        try:
            client_api = cls.load_from_json(aivk_root=aivk_root)
            logger.info("成功加载现有配置")
        except Exception as e:
            logger.warning(f"加载配置失败: {e}，使用默认配置")
        
        # 确定连接URI
        connect_uri = uri
        if uri is None:
            # 使用默认设置
            if not client_api.websocket:
                client_api.websocket = "127.0.0.1"
            
            if not client_api.websocket_port:
                client_api.websocket_port = 10143
            
            if not client_api.websocket_path:
                client_api.websocket_path = "/aivk/qq"
            
            connect_uri = client_api.uri
        
        logger.info(f"将连接到: {connect_uri}")
        
        # 连接到服务器
        websocket = None
        try:
            websocket = await asyncio.wait_for(client_api.ws_client(uri=connect_uri), timeout=timeout)
            logger.info(f"成功连接到 {connect_uri}")
            
            # 发送ping消息测试连接
            await client_api.ping
            logger.info("ping消息已发送")
            
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"连接超时: {connect_uri}")
            return False
        except ConnectionRefusedError:
            logger.error(f"连接被拒绝: {connect_uri}")
            return False
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False
        finally:
            # 确保关闭连接
            if websocket:
                try:
                    await websocket.close()
                    logger.info("连接已关闭")
                except:
                    pass



            

    # region CLI 测试 END

























    # region 无人区

























# ---------------------
# region QQ API
# ---------------------
    @property
    async def ping(self):
        await self.send("ping", self.root if self.root else self.bot_uid , message_type="private")

    async def send(self, message: str, target_id: str, message_type: str = "private", auto_escape: bool = False) -> dict:
        """
        发送消息

        :param message: 要发送的消息内容
        :param target_id: 目标ID（用户QQ号或群号，取决于message_type）
        :param message_type: 消息类型，可以为 'private'(私聊) 或 'group'(群聊)，默认为'private'
        :param auto_escape: 消息内容是否作为纯文本发送（即不解析CQ码），默认为False
        :return: 响应数据
        """
        if not self.ws_connection:
            raise Exception("没有活跃的WebSocket连接，请先建立连接")

        pass

    async def receive(self, timeout: float = None) -> dict:
        """
        接收消息（简化版）

        此方法会等待并接收一条消息，可用于监听私聊、群聊消息或其他事件

        :param timeout: 接收超时时间（秒），None表示无限等待
        :return: 解析后的消息数据字典
        :raises: Exception 如果WebSocket连接不存在或接收超时
        """
        if not self.ws_connection:
            raise Exception("没有活跃的WebSocket连接，请先建立连接")

        pass