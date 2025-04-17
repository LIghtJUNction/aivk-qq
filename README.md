# AIVK-QQ

<div align="center">
  
![AIVK-QQ Logo](https://img.shields.io/badge/AIVK--QQ-智能QQ框架-blue?style=for-the-badge&logo=tencent-qq)

[![Python Version](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/github/license/LIghtJUNction/aivk-qq)](LICENSE)

**aivk-qq 是pypi包 / uv project / aivk module / mcp server / cli tool /Napcat launcher
**集成MCP服务器、CLI工具、Napcat.Shell启动器和Napcat API SDK于一体**

</div>

## ✨ 特性

- 🤖 **全功能QQ机器人框架** - 基于AIVK生态系统构建
- 🌐 **MCP服务器集成** - 支持Model Context Protocol，轻松连接大语言模型
- 🛠️ **便捷CLI工具** - 简化配置和部署流程
- 🚀 **Napcat.Shell启动器** - 无缝启动和管理QQ客户端
- 📚 **强大的API SDK** - 简化QQ机器人开发过程

## 🚀 快速开始

### 安装

首先安装 uv 包管理器（如果尚未安装）：

```bash
pip install uv
```

然后安装项目依赖：

```bash
uv tool install aivk_qq
uv pip install -r requirements.txt
```


### 启动前准备

注意！当前版本仅支持Windows ， 其他系统请联系我或提交PR进行适配！

uv tool install aivk
aivk init # 留空或目录

aivk-qq init 
aivk-qq config -b 受控机器人qq -r 超级管理qq -w 127.0.0.1 -wp 10143 # ws_client ip:port

aivk-qq nc # 启动Napcat.Shell --shell powershell / pwsh / cmd

aivk-qq help # 查看帮助 你可以测试ws_client能否正确连接

### 配置AIVK环境

设置AIVK根目录（以下三种方式任选其一）：
aivk-qq help <command>

```bash

1. 通过命令行指定：
   ```bash
   aivk init --path /path/to/aivk/root/
   ```

2. 设置环境变量：
   ```bash
   AIVK_ROOT=/path/to/aivk/root/
   ```

3. 使用默认路径：`~/.aivk`

### 启动应用

启动AIVK-QQ（可选择指定AIVK根目录）：

```bash
aivk-qq --path /path/to/aivk/root/
```

### 配置机器人

配置机器人账号信息（配置将保存至`AIVK_ROOT/etc/qq/config.toml`）：

```bash
aivk-qq config --bot_uid <机器人QQ号> --root <超级管理员QQ号>
```

## 💼 MCP服务器配置

### 默认（stdio）模式启动

```bash
aivk-qq mcp
```

### SSE传输模式启动

```bash
aivk-qq mcp --transport sse --port 10141 --host 127.0.0.1
```

启动后，可通过以下地址访问SSE服务：
```
http://localhost:10141/sse/
```

## 📱 Napcat.Shell 启动

启动Napcat.Shell实现QQ客户端功能增强：

```bash
aivk-qq nc
```

支持以下选项：
- `-p, --path` - 指定AIVK根目录（可选）
- `-d, --debug` - 启用调试模式（可选）

## 🔧 常见问题解决

如果遇到启动问题，请尝试：
1. 确认QQ客户端已正确安装
2. 确保以管理员权限运行
3. 检查AIVK环境配置是否正确

## 🤝 参与贡献

欢迎提交Pull Request或创建Issue来改进项目！请确保遵循项目的代码规范。

## 📄 开源协议

本项目基于 [MIT 许可证](LICENSE) 开源。

## 🙏 致谢

本项目基于以下开源项目：

- [AIVK](https://github.com/LIghtJUNction/aivk) - AI虚拟内核框架
- [MCP](https://github.com/modelcontextprotocol/python-sdk) - Model Context Protocol
- [Napcat](https://github.com/RockChinQ/NapCat) - QQ客户端增强工具

感谢所有这些项目的贡献者，使本项目成为可能。
