# pyright: reportArgumentType=false,reportPrivateUsage=false,reportUnknownVariableType=false,reportUnknownParameterType=false,reportUnknownMemberType=false,reportMissingParameterType=false,reportUnusedCallResult=false
import asyncio
import os
from pathlib import Path
import shutil
import sys
import platform
from aivk.__about__ import __version__ as __aivkversion__
import click
from aivk.api import AivkIO

from ..napcat.installer import NapcatInstaller
from ..__about__ import __version__, __author__
from ..base.utils import _get_cmd

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("aivk.qq.cli")

# region 工具函数


def _update_path(path):
    if path:
        click.secho("📁 ", nl=False)
        click.secho("设置AIVK根目录为: ", fg="bright_green", nl=False)
        click.secho(f"{path}", fg="yellow")
        path = Path(path).resolve()
        AivkIO.set_aivk_root(path)
        return True
    logger.debug(f"aivk_root_input: {path}")
    return False

def _list_config(_config):
    click.secho("\n📝 当前配置:", fg="bright_green")

    # 以表格形式打印配置项
    click.secho("-"*50, fg="bright_blue")
    click.secho(f"{'参数':<20}{'值':<30}", fg="bright_blue")
    click.secho("-"*50, fg="bright_blue")
    for key, value in _config.items():
        click.secho(f"{key:<20}", fg="bright_green", nl=False)
        if value is None:
            click.secho(f"{'未设置':<30}", fg="red")
        else:
            click.secho(f"{str(value):<30}", fg="yellow")
    click.secho("-"*50, fg="bright_blue")



@click.group("aivk.qq.cli")
def cli():
    """AIVK QQ CLI"""
    pass

# region CLI

@cli.command()
@click.option("--path","-p", help="Path to the AIVK ROOT directory")
@click.option("--bot_uid", "-b", help="受控机器人的QQ号")
@click.option("--root", "-r", help="超级管理员QQ号")
def config(path, bot_uid, root):
    """
    设置基本配置
    :param path: Path to the AIVK ROOT directory
    :bot_uid: 受控机器人的QQ号
    :root : 超级管理员QQ号
    """
    click.echo("\n" + "="*50)
    click.secho("⚙️ AIVK-QQ 配置设置 ⚙️", fg="bright_cyan", bold=True)
    click.echo("="*50)

    _update_path(path)

    aivk_qq_config = AivkIO.get_config("qq")

    if not shutil.which("uv"):
        click.secho("⚠️ UV未安装", fg="bright_red")
        if click.confirm("是否前往查看教程？", default=True, abort=False):
            click.secho("CTRL+LMB: https://docs.astral.sh/uv 以获取更多信息。")

    if aivk_qq_config.get("bot_uid", None) is None and bot_uid is None:
        click.secho("⚠️ 受控机器人的QQ号未设置", fg="bright_red")
        aivk_qq_config["bot_uid"] = click.prompt("请输入受控机器人的QQ号", type=int)

    if aivk_qq_config.get("root", None) is None and root is None:
        click.secho("⚠️ 超级管理员QQ号未设置", fg="bright_red")
        aivk_qq_config["root"] = click.prompt("请输入超级管理员QQ号", type=int)
    
    if AivkIO.get_aivk_root().exists() and AivkIO.is_aivk_root():
        click.secho("📁 ", nl=False)
        click.secho("当前AIVK根目录为: ", fg="bright_green", nl=False)
        click.secho(f"{AivkIO.get_aivk_root()}", fg="yellow")
    else:
        click.secho("请使用：aivk init <path/env:AIVK_ROOT/~/.aivk> 初始化AIVK根目录！", fg="bright_red")
        if shutil.which("aivk"):
            click.secho("请使用：aivk init <path/env:AIVK_ROOT/~/.aivk> 初始化AIVK根目录！", fg="bright_red")
        else:
            if click.confirm("是否下载AIVK？", default=True, abort=False):
                from aivk.api import AivkExecuter
                asyncio.run(AivkExecuter.aexec(cmd=["uv","tool","install","aivk"], shell=True, env=os.environ))
            raise SystemExit(1)


    click.secho("\n📝 当前配置:", fg="bright_green")
    AivkIO.save_config("qq", aivk_qq_config)
    click.secho("\n✅ 配置已保存", fg="bright_green", bold=True)

    _list_config(aivk_qq_config)

    
    AivkIO.add_module_id("qq")
    
    click.echo("\n" + "="*50)
    click.secho("操作完成！", fg="bright_cyan", bold=True)
    click.echo("="*50 + "\n")

# region init
@cli.command()
@click.option("--path", "-p", help="Path to the AIVK ROOT directory")
@click.option("--force", "-f", is_flag=True, help="强制初始化")
def init(path, force ): 
    """
    初始化
    -f 强制重新下载napcat shell
    -p 指定AIVK根目录(可选)
    """
    NapcatInstaller.update_proxy_list()
    click.echo("\n" + "="*50)
    click.secho("🚀 AIVK-QQ 初始化向导 🚀", fg="bright_cyan", bold=True)
    click.echo("="*50)

    _update_path(path)

    aivk_qq_config = AivkIO.get_config("qq")

    if aivk_qq_config.get("bot_uid", None) is None or aivk_qq_config.get("root", None) is None:
        click.secho("⚠️ 受控机器人的QQ号或超级管理员QQ号未设置", fg="bright_red")
        if click.confirm("是否前往设置？/ 或者你可以稍后执行：aivk-qq config 设置", default=False, abort=False):
            aivk_qq_config["bot_uid"] = click.prompt("请输入受控机器人的QQ号", type=int)
            aivk_qq_config["root"] = click.prompt("请输入超级管理员QQ号", type=int)
    
    AivkIO.save_config("qq", aivk_qq_config)
    click.secho("\n✅ 配置已保存", fg="bright_green")
    
    AivkIO.add_module_id("qq")

    # 下载Napcat Shell
    if platform.system() == "Windows" and NapcatInstaller.need_update():
        NapcatInstaller.download_for_windows(force=force)
    else:
        click.secho("⚠️ 当前操作系统暂不支持自动下载", fg="bright_red")

    _list_config(aivk_qq_config)

# region update
@cli.command()
@click.option("--path", "-p", help="Path to the AIVK ROOT directory")
@click.option("--pwsh", "-pw", is_flag=True, help="更新powershell")
@click.option("--force", "-f", is_flag=True, help="强制重新下载，即使已是最新版本")
def update(path, pwsh, force ):
    """
    更新napcat shell
    -p 指定AIVK根目录(可选)
    -f 强制重新下载，即使已是最新版本
    --proxy 指定下载代理服务器URL
    """
    NapcatInstaller.update_proxy_list()
    click.echo("\n" + "="*50)
    click.secho("🔄 AIVK-QQ 更新向导 🔄", fg="bright_cyan", bold=True)
    click.echo("="*50)

    _update_path(path)

    # 如果需要，更新PowerShell
    if platform.system() == "Windows" and pwsh and shutil.which("winget"):
        click.secho("🔄 正在更新PowerShell...", fg="bright_magenta")
        from aivk.api import AivkExecuter
        asyncio.run(AivkExecuter.aexec(
            cmd=["winget", "install", "--id", "Microsoft.PowerShell", "--source", "winget"],
            shell=True,
            env=os.environ
        ))
        click.secho("✅ PowerShell更新完成", fg="bright_green")

    click.secho("🔍 检查NapCat.Shell版本...", fg="bright_blue")
    
    if NapcatInstaller.need_update():
        click.secho("🔄 需要更新NapCat.Shell...", fg="bright_yellow")
        if platform.system() == "Windows":
            NapcatInstaller.download_for_windows(force=force)
        else:
            
            click.secho("⚠️ 当前操作系统暂不支持自动下载", fg="bright_red")
        click.echo("\n" + "="*50)
        click.secho("🎉 更新完成！", fg="bright_cyan", bold=True)
        click.echo("="*50 + "\n")

    click.secho("无需更新NapCat.Shell", fg="bright_green")
    click.echo("\n" + "="*50)



# region nc(napcat)

"""
aivk-qq nc --shell <?>
            系统终端        VSCODE终端
cmd         正常            正常
pwsh        正常            正常
powershell  正常            异常 (☠️)

"""

@cli.command()
@click.option("--path", "-p", help="Path to the AIVK ROOT directory")
@click.option("--shell", "-s", type=click.Choice(["cmd", "powershell", "pwsh"]), default="pwsh", help="cmd : 远古版cmd , powershell : 现代版powershell 5.10 , pwsh : 现代版powershell7")
@click.option("--title", "-t", default="NapCat.shell", help="设置窗口标题")
@click.argument("qq", required=False, default=None)
def nc(path, qq, shell, title):
    """
    启动NapCat.Shell
    \b
    aivk-qq nc --shell <?>
    \n
                    系统终端        VSCODE终端 \b
    \n        
    cmd         正常            正常
    \n
         pwsh        正常            正常 (☑️ 推荐)
    \n
         powershell  正常            异常 (☠️)

    """
    from aivk.api import AivkExecuter
    _update_path(path)
    if shell != "pwsh":
        click.secho(message="⚠️ 推荐pwsh ", fg="bright_red")
        if click.confirm(text="是否安装pwsh(powershell7)", default=True, abort=False):
            asyncio.run(main=AivkExecuter.aexec(cmd=["winget" , "install" , "--id" , "Microsoft.PowerShell" , "--source" , "winget"] , shell=True , env=os.environ))
            click.secho(message="✅ pwsh安装完成", fg="bright_green")   
            
    _cmd ="./launcher.bat" if not qq else f"launcher.bat {qq}"
    cmd = _get_cmd(shell_type=shell, title=title ,cwd=str(AivkIO.get_aivk_root() / "data" / "qq" / "napcat" ), cmd=_cmd)

    asyncio.run(AivkExecuter.aexec(cmd=cmd, shell=True, env=os.environ, cwd=str(AivkIO.get_aivk_root() / "data" / "qq"  )))



# region version
@cli.command()
@click.option("--path", "-p", help="Path to the AIVK ROOT directory")
def version(path):
    """显示当前版本信息"""
    
    _update_path(path)
    
    click.echo("\n" + "="*50)
    click.secho("🌟 AIVK-QQ 信息面板 🌟", fg="bright_cyan", bold=True)
    click.echo("="*50)
    
    # Napcat.Shell 版本
    dotVersion = AivkIO.get_aivk_root() / "data" / "qq" / "napcat_root" / ".version"

    if dotVersion.exists():
        with open(dotVersion) as f:
            version = f.read().strip()
            click.secho("🤖 Napcat.Shell 版本: ", fg="bright_green", nl=False)
            click.secho(f"{version}", fg="yellow", bold=True)
    else:
        click.secho("⚠️ Napcat.Shell 未安装或版本文件不存在", fg="bright_red")

    # AIVK-QQ 版本信息
    click.secho("📦 AIVK-QQ 版本: ", fg="bright_green", nl=False)
    click.secho(f"{__version__}", fg="yellow", bold=True)

    click.secho("📦 AIVK 版本: ", fg="bright_green", nl=False)
    click.secho(f"{__aivkversion__}", fg="yellow", bold=True)
    
    click.secho("👤 开发作者: ", fg="bright_green", nl=False)
    click.secho(f"{__author__}", fg="magenta")
    
    click.echo("\n" + "-"*50)
    click.secho("🖥️ 系统信息", fg="bright_cyan", bold=True)
    click.echo("-"*50)
    
    # Python信息
    click.secho("🐍 Python版本: ", fg="bright_green", nl=False)
    click.secho(f"{platform.python_version()}", fg="yellow")
    
    # 系统信息
    click.secho("💻 操作系统: ", fg="bright_green", nl=False) 
    click.secho(f"{platform.system()} {platform.release()}", fg="yellow")
    
    click.secho("🔧 系统架构: ", fg="bright_green", nl=False)
    click.secho(f"{platform.architecture()[0]}", fg="yellow")
    
    click.secho("🌐 系统平台: ", fg="bright_green", nl=False)
    click.secho(f"{platform.platform()}", fg="yellow")
    
    click.secho("📋 系统版本: ", fg="bright_green", nl=False)
    click.secho(f"{platform.version()}", fg="yellow")
    
    click.secho("🏠 主机名称: ", fg="bright_green", nl=False)
    click.secho(f"{platform.uname().node}", fg="yellow")
    
    click.secho("⚙️ 处理器: ", fg="bright_green", nl=False)
    click.secho(f"{platform.processor()}", fg="yellow")
    
    click.echo("\n" + "="*50)
    click.secho("感谢使用 AIVK-QQ！", fg="bright_cyan", bold=True)
    click.echo("="*50 + "\n")

    
# region mcp
@cli.command()
@click.option("--port", "-p", help="MCP服务器端口")
@click.option("--host", "-h", help="MCP服务器地址")
@click.option("--transport", "-t", type=click.Choice(['sse', 'stdio']), default="stdio", help="MCP服务器传输协议") # 二选一选项
def mcp(port, host, transport):
    """
    启动MCP服务器
    """
    click.echo("\n" + "="*50)
    click.secho("🖥️ AIVK-QQ MCP服务器 🖥️", fg="bright_cyan", bold=True)
    click.echo("="*50)
    
    aivk_qq_config = AivkIO.get_config("qq")
    
    click.secho("⚙️ 配置MCP服务器参数...", fg="bright_blue")
    
    if port:
        click.secho("🔌 ", nl=False)
        click.secho("设置MCP服务器端口为: ", fg="bright_green", nl=False)
        click.secho(f"{port}", fg="yellow")
        port = int(port)
        aivk_qq_config["port"] = port
        
    if host:
        click.secho("🌐 ", nl=False)
        click.secho("设置MCP服务器地址为: ", fg="bright_green", nl=False)
        click.secho(f"{host}", fg="yellow")
        aivk_qq_config["host"] = host
    
    if transport:
        click.secho("📡 ", nl=False)
        click.secho("设置MCP服务器传输协议为: ", fg="bright_green", nl=False)
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


# region help
@cli.command(name="help")
@click.argument("command_name", required=False)
def help_cmd(command_name):
    """Show help information for commands
    
    If COMMAND_NAME is provided, show detailed help for that command.
    Otherwise, show general help information.
    """
    ctx = click.get_current_context()
    
    click.echo("\n" + "="*50)
    click.secho("💡 AIVK-QQ 命令帮助 💡", fg="bright蓝", bold=True)
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
        click.secho(f"{'命令':<15}{'描述':<35}", fg="bright蓝")
        click.secho("-"*50, fg="bright蓝")
        for cmd_name, help_text in commands:
            click.secho(f"{cmd_name:<15}", fg="bright_yellow", nl=False)
            click.secho(f"{help_text:<35}", fg="white")
        
        click.echo("\n" + "-"*50)
        click.secho("💡 提示: 使用 'aivk-qq help <命令>' 查看特定命令的详细帮助", fg="bright蓝")
        
    click.echo("\n" + "="*50)
    click.secho("感谢使用 AIVK-QQ！", fg="bright蓝", bold=True)
    click.echo("="*50 + "\n")

