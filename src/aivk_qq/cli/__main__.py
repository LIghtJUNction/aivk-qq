# -*- coding: utf-8 -*-
import asyncio
from pathlib import Path
import shutil
import sys
import platform
import click
from aivk.api import AivkIO

from ..__about__ import __version__, __author__

import logging

logger = logging.getLogger("aivk.qq.cli")

@click.group("aivk.qq.cli")
def cli():
    """AIVK QQ CLI"""
    pass

@cli.command()
@click.option("--path","-p", help="Path to the AIVK ROOT directory")
@click.option("--bot_uid", "-b", help="受控机器人的QQ号")
@click.option("--root", "-r", help="超级管理员QQ号")
@click.option("--websocket", "-w", help="ws 地址")
@click.option("--websocket_port", "-wp", help="ws 端口")
def config(path, bot_uid, root, websocket, websocket_port):
    """
    设置基本配置
    :param path: Path to the AIVK ROOT directory
    :bot_uid: 受控机器人的QQ号
    :root : 超级管理员QQ号
    :websocket: ws 地址
    :websocket_port: ws 端口
    """
    click.echo("\n" + "="*50)
    click.secho(f"⚙️ AIVK-QQ 配置设置 ⚙️", fg="bright_cyan", bold=True)
    click.echo("="*50)

    if path:
        click.secho("📁 ", nl=False)
        click.secho(f"设置AIVK根目录为: ", fg="bright_green", nl=False)
        click.secho(f"{path}", fg="yellow")
        path = Path(path).resolve()
        AivkIO.set_aivk_root(path)

    aivk_qq_config = AivkIO.get_config("qq")
    aivk_qq_config["bot_uid"] = bot_uid if bot_uid else aivk_qq_config.get("bot_uid", None)
    aivk_qq_config["root"] = root if root else aivk_qq_config.get("root", None)
    aivk_qq_config["websocket"] = websocket if websocket else aivk_qq_config.get("websocket", None)
    aivk_qq_config["websocket_port"] = websocket_port if websocket_port else aivk_qq_config.get("websocket_port", None)
    
    
    click.secho("\n📝 当前配置:", fg="bright_green")
    
    # 以表格形式打印配置项
    click.secho("-"*50, fg="bright_blue")
    click.secho(f"{'参数':<20}{'值':<30}", fg="bright_blue")
    click.secho("-"*50, fg="bright_blue")
    for key, value in aivk_qq_config.items():
        click.secho(f"{key:<20}", fg="bright_green", nl=False)
        if value is None:
            click.secho(f"{'未设置':<30}", fg="red")
        else:
            click.secho(f"{str(value):<30}", fg="yellow")
    click.secho("-"*50, fg="bright_blue")
    
    AivkIO.save_config("qq", aivk_qq_config)
    click.secho("\n✅ 配置已保存", fg="bright_green", bold=True)
    AivkIO.add_module_id("qq")
    
    click.echo("\n" + "="*50)
    click.secho("操作完成！", fg="bright_cyan", bold=True)
    click.echo("="*50 + "\n")

@cli.command()
@click.option("--path", "-p", help="Path to the AIVK ROOT directory")
@click.option("--force", "-f", is_flag=True, help="强制初始化")
@click.option("--bot_uid", "-b", help="受控机器人的QQ号")
@click.option("--root", "-r", help="超级管理员QQ号")
@click.option("--websocket", "-w", help="ws 地址")
@click.option("--websocket_port", "-wp", help="ws 端口")
def init(path, force, bot_uid, root, websocket, websocket_port):
    """
    初始化
    -f 强制重新下载napcat shell
    -p 指定AIVK根目录(可选)
    """
    click.echo("\n" + "="*50)
    click.secho(f"🚀 AIVK-QQ 初始化向导 🚀", fg="bright_cyan", bold=True)
    click.echo("="*50)

    if path:
        click.secho("📁 ", nl=False)
        click.secho(f"设置AIVK根目录为: ", fg="bright_green", nl=False)
        click.secho(f"{path}", fg="yellow")
        path = Path(path).resolve()
        AivkIO.set_aivk_root(path)

    aivk_qq_config = AivkIO.get_config("qq")
    qq_data_path = AivkIO.get_aivk_root() / "data" / "qq"
    napcat_root = qq_data_path / "napcat_root"

    if force:
        click.secho("🔄 强制初始化模式", fg="bright_red", bold=True)
        click.secho("删除现有 Napcat.Shell...", fg="bright_yellow")
        shutil.rmtree(napcat_root, ignore_errors=True)
        click.secho("✅ 已清理旧文件", fg="bright_green")

    # 更新配置
    aivk_qq_config["bot_uid"] = bot_uid if bot_uid else aivk_qq_config.get("bot_uid", None)
    aivk_qq_config["root"] = root if root else aivk_qq_config.get("root", None)
    aivk_qq_config["websocket"] = websocket if websocket else aivk_qq_config.get("websocket", None)
    aivk_qq_config["websocket_port"] = websocket_port if websocket_port else aivk_qq_config.get("websocket_port", None)

    click.secho("\n📝 当前配置:", fg="bright_green")
    
    # 以表格形式打印配置项
    click.secho("-"*50, fg="bright_blue")
    click.secho(f"{'参数':<20}{'值':<30}", fg="bright_blue")
    click.secho("-"*50, fg="bright_blue")
    for key, value in aivk_qq_config.items():
        click.secho(f"{key:<20}", fg="bright_green", nl=False)
        if value is None:
            click.secho(f"{'未设置':<30}", fg="red")
        else:
            click.secho(f"{str(value):<30}", fg="yellow")
    click.secho("-"*50, fg="bright_blue")
    
    AivkIO.save_config("qq", aivk_qq_config)
    click.secho("\n✅ 配置已保存", fg="bright_green")
    AivkIO.add_module_id("qq")

    # 创建目录结构
    click.secho("\n📂 初始化文件系统...", fg="bright_magenta")

    # 检查napcat_root目录是否存在
    if not napcat_root.exists() or not any(napcat_root.iterdir()):
        napcat_root.mkdir(parents=True, exist_ok=True)
        click.secho(f"✅ 创建目录: {napcat_root}", fg="bright_green")
        from ..napcat.api import NapcatAPI
        napcat_api = NapcatAPI(napcat_root=napcat_root, bot_uid=bot_uid, root=root, websocket=websocket, websocket_port=websocket_port)
        click.secho("✅ 创建新配置", fg="bright_green")
    else:
        from ..napcat.api import NapcatAPI
        # 如果目录已存在，尝试加载配置或创建新实例
        try:
            click.secho("🔄 加载现有配置...", fg="bright_yellow")
            napcat_api = NapcatAPI.load_from_json(napcat_root=napcat_root)
            # 更新可能变化的配置
            napcat_api.bot_uid = bot_uid if bot_uid else aivk_qq_config.get("bot_uid", None)
            napcat_api.root = root if root else aivk_qq_config.get("root", None)
            napcat_api.websocket = websocket if websocket else aivk_qq_config.get("websocket", None)
            napcat_api.websocket_port = websocket_port if websocket_port else aivk_qq_config.get("websocket_port", None)
            click.secho("✅ 配置已更新", fg="bright_green")
        
        except Exception as e:
            click.secho(f"⚠️ 加载配置失败: {e}", fg="bright_red")
            click.secho("🔄 创建新配置...", fg="bright_yellow")
            napcat_api = NapcatAPI(napcat_root=napcat_root, bot_uid=bot_uid, root=root, websocket=websocket, websocket_port=websocket_port)
            click.secho("✅ 创建新配置成功", fg="bright_green")

    click.secho("\n🌐 设置代理...", fg="bright_magenta")
    napcat_api.set_proxy("https://ghfast.top/")
    click.secho("✅ 代理已设置为: https://ghfast.top/", fg="bright_green")
    
    # 目录为空时下载napcat shell
    if not any(napcat_root.iterdir()):
        click.secho("\n📥 正在下载 Napcat.Shell...", fg="bright_magenta", bold=True)
        try:
            if platform.system() == "Windows":
                napcat_api.download_for_win()
                logger.info(f"Napcat.Shell 已下载到AIVK_ROOT : {napcat_root}")
                click.secho(f"✅ Napcat.Shell 下载成功！保存位置: {napcat_root}", fg="bright_green", bold=True)
            elif platform.system() == "Linux":
                click.secho("⚠️ 自立自强，Linux用户请自行下载", fg="bright_yellow", bold=True)
                napcat_api.download_for_linux()
                logger.info(f"Napcat.Shell 已下载到AIVK_ROOT : {napcat_root}")
            else:
                click.secho("❌ 不支持的操作系统", fg="bright_red", bold=True)
                sys.exit(1)
        except Exception as e:
            click.secho(f"❌ 下载失败: {e}", fg="bright_red", bold=True)
            sys.exit(1)
    else:
        logger.info(f"Napcat.Shell 已存在于AIVK_ROOT : {napcat_root} , 使用 -f 强制初始化")
        click.secho(f"ℹ️ Napcat.Shell 已存在于: {napcat_root}", fg="bright_blue")
        click.secho("💡 提示: 使用 -f 参数可强制重新下载", fg="bright_blue", italic=True)
    
    # 保存配置
    napcat_api.save_to_json()
    click.secho("\n✅ 配置已保存到磁盘", fg="bright_green")
    
    click.echo("\n" + "="*50)
    click.secho("🎉 初始化完成！", fg="bright_cyan", bold=True)
    click.echo("="*50 + "\n")

@cli.command()
@click.option("--path", "-p", help="Path to the AIVK ROOT directory")
def update(path):
    """
    更新napcat shell
    -p 指定AIVK根目录(可选)
    """
    click.echo("\n" + "="*50)
    click.secho(f"🔄 AIVK-QQ 更新向导 🔄", fg="bright_cyan", bold=True)
    click.echo("="*50)

    if path:
        click.secho("📁 ", nl=False)
        click.secho(f"设置AIVK根目录为: ", fg="bright_green", nl=False)
        click.secho(f"{path}", fg="yellow")
        path = Path(path).resolve()
        AivkIO.set_aivk_root(path)

    aivk_qq_config = AivkIO.get_config("qq")
    qq_data_path = AivkIO.get_aivk_root() / "data" / "qq"
    napcat_root = qq_data_path / "napcat_root"

    from ..napcat.api import NapcatAPI

    click.secho("🔍 检查配置...", fg="bright_blue")
    try:
        napcat_api = NapcatAPI.load_from_json(napcat_root=napcat_root)
        click.secho("✅ 配置加载成功", fg="bright_green")
    except Exception as e:
        click.secho(f"⚠️ 配置加载失败: {e}", fg="bright_red")
        click.secho("❌ 更新失败！请先运行 init 命令初始化", fg="bright_red", bold=True)
        sys.exit(1)

    click.secho("\n📥 正在检查 Napcat.Shell 更新...", fg="bright_magenta", bold=True)

    if napcat_api.need_update:
        click.secho("🆕 发现新版本，开始更新...", fg="bright_yellow")
        if platform.system() == "Windows":
            with click.progressbar(length=100, label="下载进度") as bar:
                def progress_callback(percent):
                    bar.update(percent - bar.pos)
                
                napcat_api.download_for_win(force=True, progress_callback=progress_callback)
                
            logger.info(f"Napcat.Shell 已更新到AIVK_ROOT : {napcat_root}")
            click.secho(f"✅ Napcat.Shell 更新完成！位置: {napcat_root}", fg="bright_green", bold=True)
        elif platform.system() == "Linux":
            click.secho("⚠️ 自立自强，Linux用户请自行下载", fg="bright_yellow", bold=True)
            napcat_api.download_for_linux()
            logger.info(f"Napcat.Shell 已更新到AIVK_ROOT : {napcat_root}")
        else:
            click.secho("❌ 不支持的操作系统", fg="bright_red", bold=True)
            sys.exit(1)
    else:
        click.secho("✅ Napcat.Shell 已是最新版本", fg="bright_green", bold=True)
    
    # 保存更新后的配置
    napcat_api.save_to_json()
    click.secho("\n💾 配置已保存到磁盘", fg="bright_green")
    
    click.echo("\n" + "="*50)
    click.secho("🎉 更新检查完成！", fg="bright_cyan", bold=True)
    click.echo("="*50 + "\n")




@cli.command()
@click.option("--path", "-p", help="Path to the AIVK ROOT directory")
def nc(path):
    """
    检查Napcat.Shell是否存在
    -p 指定AIVK根目录(可选)
    存在则启动
    """
    click.secho("🔍 Napcat.Shell 检查中...", fg="bright_blue")
    if path:
        click.secho("📁 ", nl=False)
        click.secho(f"设置AIVK根目录为: ", fg="bright_green", nl=False)
        click.secho(f"{path}", fg="yellow")
        path = Path(path).resolve()
        AivkIO.set_aivk_root(path)
    
    napcat_root = AivkIO.get_aivk_root() / "data" / "qq" / "napcat_root"
    click.secho(f"🔍 检查 Napcat.Shell 是否存在于: {napcat_root}", fg="bright_blue")
    if napcat_root.exists() and any(napcat_root.iterdir()):
        click.secho("✅ Napcat.Shell 存在", fg="bright_green")
    else:
        click.secho("❌ Napcat.Shell 不存在，请先运行 init 命令初始化", fg="bright_red", bold=True)
        sys.exit(1)

    from aivk.api import AivkExecuter
    if platform.system() == "Windows":
        command = [str(napcat_root / "napcat" / "launcher.bat")]
    elif platform.system() == "Linux":
        command = "你得自己写"
    else:
        click.secho("❌ 不支持的操作系统", fg="bright_red", bold=True)
        sys.exit(1)

    asyncio.run(AivkExecuter.aexec(command=command, shell=True , cwd=napcat_root))
  




    click.secho("✅ Napcat.Shell 启动成功", fg="bright_green")



@cli.command()
@click.option("--path", "-p", help="Path to the AIVK ROOT directory")
def version(path):
    """显示当前版本信息"""
    from ..__about__ import __version__, __author__
    
    if path:
        click.echo(f"设置AIVK根目录为: {path}")
        path = Path(path).resolve()
        AivkIO.set_aivk_root(path)
    
    click.echo("\n" + "="*50)
    click.secho(f"🌟 AIVK-QQ 信息面板 🌟", fg="bright_cyan", bold=True)
    click.echo("="*50)
    
    # Napcat.Shell 版本
    dotVersion = AivkIO.get_aivk_root() / "data" / "qq" / "napcat_root" / ".version"

    if dotVersion.exists():
        with open(dotVersion, "r") as f:
            version = f.read().strip()
            click.secho(f"🤖 Napcat.Shell 版本: ", fg="bright_green", nl=False)
            click.secho(f"{version}", fg="yellow", bold=True)
    else:
        click.secho(f"⚠️ Napcat.Shell 未安装或版本文件不存在", fg="bright_red")

    # AIVK-QQ 版本信息
    click.secho(f"📦 AIVK-QQ 版本: ", fg="bright_green", nl=False)
    click.secho(f"{__version__}", fg="yellow", bold=True)
    
    click.secho(f"👤 开发作者: ", fg="bright_green", nl=False)
    click.secho(f"{__author__}", fg="magenta")
    
    click.echo("\n" + "-"*50)
    click.secho("🖥️ 系统信息", fg="bright_cyan", bold=True)
    click.echo("-"*50)
    
    # Python信息
    click.secho(f"🐍 Python版本: ", fg="bright_green", nl=False)
    click.secho(f"{platform.python_version()}", fg="yellow")
    
    # 系统信息
    click.secho(f"💻 操作系统: ", fg="bright_green", nl=False) 
    click.secho(f"{platform.system()} {platform.release()}", fg="yellow")
    
    click.secho(f"🔧 系统架构: ", fg="bright_green", nl=False)
    click.secho(f"{platform.architecture()[0]}", fg="yellow")
    
    click.secho(f"🌐 系统平台: ", fg="bright_green", nl=False)
    click.secho(f"{platform.platform()}", fg="yellow")
    
    click.secho(f"📋 系统版本: ", fg="bright_green", nl=False)
    click.secho(f"{platform.version()}", fg="yellow")
    
    click.secho(f"🏠 主机名称: ", fg="bright_green", nl=False)
    click.secho(f"{platform.uname().node}", fg="yellow")
    
    click.secho(f"⚙️ 处理器: ", fg="bright_green", nl=False)
    click.secho(f"{platform.processor()}", fg="yellow")
    
    click.echo("\n" + "="*50)
    click.secho("感谢使用 AIVK-QQ！", fg="bright_cyan", bold=True)
    click.echo("="*50 + "\n")

    
@cli.command()
@click.option("--port", "-p", help="MCP服务器端口")
@click.option("--host", "-h", help="MCP服务器地址")
@click.option("--transport", "-t", type=click.Choice(['sse', 'stdio']), default="stdio", help="MCP服务器传输协议") # 二选一选项
def mcp(port, host, transport):
    """
    启动MCP服务器
    """
    click.echo("\n" + "="*50)
    click.secho(f"🖥️ AIVK-QQ MCP服务器 🖥️", fg="bright_cyan", bold=True)
    click.echo("="*50)
    
    aivk_qq_config = AivkIO.get_config("qq")
    
    click.secho("⚙️ 配置MCP服务器参数...", fg="bright_blue")
    
    if port:
        click.secho("🔌 ", nl=False)
        click.secho(f"设置MCP服务器端口为: ", fg="bright_green", nl=False)
        click.secho(f"{port}", fg="yellow")
        port = int(port)
        aivk_qq_config["port"] = port
    if host:
        click.secho("🌐 ", nl=False)
        click.secho(f"设置MCP服务器地址为: ", fg="bright_green", nl=False)
        click.secho(f"{host}", fg="yellow")
        aivk_qq_config["host"] = host
    
    if transport:
        click.secho("📡 ", nl=False)
        click.secho(f"设置MCP服务器传输协议为: ", fg="bright_green", nl=False)
        click.secho(f"{transport}", fg="yellow")
        aivk_qq_config["transport"] = transport
    
    click.secho("\n📝 当前配置:", fg="bright_green")
    
    # 以表格形式打印配置项
    click.secho("-"*50, fg="bright_blue")
    click.secho(f"{'参数':<20}{'值':<30}", fg="bright_blue")
    click.secho("-"*50, fg="bright_blue")
    for key, value in aivk_qq_config.items():
        click.secho(f"{key:<20}", fg="bright_green", nl=False)
        if value is None:
            click.secho(f"{'未设置':<30}", fg="red")
        else:
            click.secho(f"{str(value):<30}", fg="yellow")
    click.secho("-"*50, fg="bright_blue")
    
    AivkIO.save_config("qq", aivk_qq_config)
    click.secho("\n✅ 配置已保存", fg="bright_green")
    AivkIO.add_module_id("qq")
    
    click.echo("\n" + "-"*50)
    click.secho("🚀 启动MCP服务器...", fg="bright_magenta", bold=True)
    click.echo("-"*50 + "\n")
    
    from ..mcp import mcp
    mcp.run(transport=transport)

@cli.command(name="help")
@click.argument("command_name", required=False)
def help_cmd(command_name):
    """Show help information for commands
    
    If COMMAND_NAME is provided, show detailed help for that command.
    Otherwise, show general help information.
    """
    ctx = click.get_current_context()
    
    click.echo("\n" + "="*50)
    click.secho(f"💡 AIVK-QQ 命令帮助 💡", fg="bright_cyan", bold=True)
    click.echo("="*50)
    
    if command_name:
        # 查找指定命令
        command = cli.get_command(ctx, command_name)
        if command:
            click.secho(f"📚 '{command_name}' 命令详细帮助:", fg="bright_green")
            click.echo("-"*50)
            # 显示特定命令的帮助信息
            help_text = command.get_help(ctx)
            
            # 美化帮助输出
            lines = help_text.split('\n')
            for line in lines:
                if line.strip().startswith('Usage:'):
                    click.secho(line, fg="bright_yellow", bold=True)
                elif line.strip().startswith('Options:'):
                    click.secho(line, fg="bright_magenta", bold=True)
                elif '--' in line:
                    parts = line.split('  ')
                    if len(parts) >= 2:
                        option = parts[0].strip()
                        desc = '  '.join(parts[1:]).strip()
                        click.secho(f"{option}", fg="bright_blue", nl=False)
                        click.secho(f"  {desc}", fg="bright_white")
                    else:
                        click.echo(line)
                else:
                    click.echo(line)
        else:
            click.secho(f"❌ 未知命令: {command_name}", fg="bright_red", bold=True)
            click.secho("请使用 help 命令查看所有可用命令", fg="yellow")
            sys.exit(1)
    else:
        # 显示通用帮助信息与可用命令列表
        click.secho("📋 可用命令列表:", fg="bright_green", bold=True)
        click.echo("-"*50)
        
        # 获取所有命令
        commands = []
        for cmd_name in sorted(cli.list_commands(ctx)):
            cmd = cli.get_command(ctx, cmd_name)
            if cmd is not None:
                help_text = cmd.get_short_help_str()
                commands.append((cmd_name, help_text))
        
        # 显示命令列表
        click.secho(f"{'命令':<15}{'描述':<35}", fg="bright_blue")
        click.secho("-"*50, fg="bright_blue")
        for cmd_name, help_text in commands:
            click.secho(f"{cmd_name:<15}", fg="bright_yellow", nl=False)
            click.secho(f"{help_text:<35}", fg="white")
        
        click.echo("\n" + "-"*50)
        click.secho("💡 提示: 使用 'aivk-qq help <命令>' 查看特定命令的详细帮助", fg="bright_cyan")
        
    click.echo("\n" + "="*50)
    click.secho("感谢使用 AIVK-QQ！", fg="bright_cyan", bold=True)
    click.echo("="*50 + "\n")
