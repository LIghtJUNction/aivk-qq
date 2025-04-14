from pathlib import Path
import shutil
import sys
import click
from aivk.api import AivkIO

from ..base.utils import setup_napcat
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
def config(path, bot_uid, root):
    """
    设置基本配置
    :param path: Path to the AIVK ROOT directory
    :bot_uid: 受控机器人的QQ号
    :root : 超级管理员QQ号
    """
    if path:
        click.echo(f"设置AIVK根目录为: {path}")
        path = Path(path).resolve()
        AivkIO.set_aivk_root(path)

    aivk_qq_config = AivkIO.get_config("qq")
    aivk_qq_config["bot_uid"] = bot_uid if bot_uid else aivk_qq_config.get("bot_uid", None)
    aivk_qq_config["root"] = root if root else aivk_qq_config.get("root", None)
    click.echo(f"当前配置: {aivk_qq_config}")
    AivkIO.save_config("qq", aivk_qq_config)
    click.echo("配置已保存")
    AivkIO.add_module_id("qq")

@cli.command()
@click.option("--force", "-f", is_flag=True, help="强制重新安装napcat")
def init(force):
    """
    初次运行时执行的初始化操作
    下载napcat程序
    登录QQ账号
    """
    aivk_qq_config = AivkIO.get_config("qq")
    if not aivk_qq_config.get("bot_uid", None):
        click.echo("请先设置受控机器人的QQ号")
        sys.exit(1)
    if not aivk_qq_config.get("root", None):
        click.echo("请先设置超级管理员QQ号")
        sys.exit(1)
    
    ncat_dir : Path = AivkIO.get_aivk_root() / "data" / "qq" / "napcat"
    logger.info(f"QQ 数据目录: {ncat_dir}")

    if force:
        click.echo("强制重新安装napcat")
        shutil.rmtree(ncat_dir, ignore_errors=True)

    bot = setup_napcat()
    bot.run()
    logger.info("NcatBot 服务启动完毕")
    
@cli.command()
@click.option("--port", "-p", help="MCP服务器端口")
@click.option("--host", "-h", help="MCP服务器地址")
@click.option("--transport", "-t", type=click.Choice(['sse', 'stdio']), default="stdio", help="MCP服务器传输协议") # 二选一选项
def mcp(port, host, transport):
    """
    启动MCP服务器
    """
    aivk_qq_config = AivkIO.get_config("qq")
    if port:
        click.echo(f"设置MCP服务器端口为: {port}")
        port = int(port)
        aivk_qq_config["port"] = port
    if host:
        click.echo(f"设置MCP服务器地址为: {host}")
        aivk_qq_config["host"] = host
    
    if transport:
        click.echo(f"设置MCP服务器传输协议为: {transport}")
        aivk_qq_config["transport"] = transport
    click.echo(f"当前配置: {aivk_qq_config}")
    AivkIO.save_config("qq", aivk_qq_config)
    click.echo("配置已保存")
    AivkIO.add_module_id("qq")
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
    if command_name:
        # 查找指定命令
        command = cli.get_command(ctx, command_name)
        if command:
            # 显示特定命令的帮助信息
            click.echo(command.get_help(ctx))
        else:
            click.echo(f"Unknown command: {command_name}")
            sys.exit(1)
    else:
        # 显示通用帮助信息
        click.echo(cli.get_help(ctx))
