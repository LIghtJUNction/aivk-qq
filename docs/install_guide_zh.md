# AIVK-QQ 安装指南

## 环境要求
- Python ≥3.13
- UV 包管理器
- Windows/Linux/macOS 系统

## 安装步骤

### 1. 安装 UV 工具链
```powershell
# Windows
irm https://astral.sh/uv/install.ps1 | iex

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 克隆仓库
```bash
git clone https://github.com/lightjuncion/aivk-qq.git
cd aivk-qq
```

### 3. 创建虚拟环境
```bash
uv venv .venv
```

### 4. 激活环境
```powershell
# Windows
.\.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 5. 安装依赖
```bash
uv pip install -e ".[dev]"
```

## 验证安装
```bash
aivk-qq --version
# 预期输出: aivk-qq 0.1.4.0

pytest --version
# 应显示 pytest 8.x 版本
```

## 常见问题
### Q1: 安装时出现SSL错误
```bash
uv pip install --pip-options "--trusted-host pypi.org --trusted-host files.pythonhosted.org" [package]
```

### Q2: 虚拟环境激活失败
- Windows: 执行 `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
- 检查系统路径是否包含 `.venv/Scripts`

## 依赖清单
| 包名称       | 版本要求    | 功能描述                 |
|--------------|-------------|--------------------------|
| aiohttp      | ≥3.11.16    | 异步HTTP客户端           |
| httpx        | ≥0.28.1     | 同步/异步混合HTTP客户端  |
| websockets   | ≥15.0.1     | WebSocket 通信支持       |
| mcp[cli]     | ≥1.6.0      | MCP服务器核心依赖        |
