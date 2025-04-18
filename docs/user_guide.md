# AIVK-QQ 用户手册

## 快速入门
1. 安装SDK
```bash
uv pip install aivk-qq
```

2. 运行示例
```python
from aivk_qq.napcat import QQBot

bot = QQBot()
bot.start()
```

## 详细安装指南
### 环境要求
- Python 3.11+
- UV包管理器 0.1.0+

### 开发依赖安装
```bash
uv pip install "aivk-qq[dev]" --python python3.11
```

## 基础配置
```python
# config.py
MCP_SERVER = "localhost:8080"
API_TIMEOUT = 30
