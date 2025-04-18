# 弃用与迁移指南（Deprecation and Migration Guide）

本文档详细说明Nacpat SDK中已弃用的功能及其替代方案。

## 目录
- [弃用与迁移指南（Deprecation and Migration Guide）](#弃用与迁移指南deprecation-and-migration-guide)
  - [目录](#目录)
  - [类型注解更新（Type Annotation Updates）](#类型注解更新type-annotation-updates)
  - [类属性声明规范（Class Attribute Declaration Standards）](#类属性声明规范class-attribute-declaration-standards)
  - [Pyright 类型检查解决方案（Pyright Type Checking Solutions）](#pyright-类型检查解决方案pyright-type-checking-solutions)
    - [1. 弃用Optional类型（Deprecating Optional Type）](#1-弃用optional类型deprecating-optional-type)
    - [2. 清理未使用导入（Cleaning Unused Imports）](#2-清理未使用导入cleaning-unused-imports)
    - [3. 避免使用Any类型（Avoiding Any Type）](#3-避免使用any类型avoiding-any-type)
    - [4. 类属性类型注解（Class Attribute Type Annotations）](#4-类属性类型注解class-attribute-type-annotations)
  - [日志级别类型约束（Log Level Type Constraints）](#日志级别类型约束log-level-type-constraints)
- [不安全写法](#不安全写法)
- [类型安全写法](#类型安全写法)

## 类型注解更新（Type Annotation Updates）
```python
# 弃用写法
from typing import Optional, Union

# 推荐写法
def new_style(param: int | None) -> str | bytes:
    pass
```

## 类属性声明规范（Class Attribute Declaration Standards）
```python
# 旧式声明
class NapcatAPI:
    def __init__(self):
        self.http_client = NapcatHttpClient()  # 缺少类型提示

# 新式声明
class NapcatAPI:
    http_client: NapcatHttpClient  # 类级类型注解
    
    def __init__(self):
        self.http_client = NapcatHttpClient()
```

## v2.0 迁移指南

### 主要变更
1. **包管理工具迁移**：
   ```bash
   # 旧版pip命令
   pip install aivk-qq[all]
   
   # 新版uv命令
   uv pip install "aivk-qq[all]" --python python3.11
   ```

2. **MCP服务配置变更**：
   ```python
   # v1.x 配置方式
   from aivk_qq import MCPServer
   
   # v2.x 配置方式
   from aivk_qq.mcp.server import MCPServer
   ```

3. **事件类型强化**：
   ```python
   # 旧版通用事件类型
   from typing import Any
   def handle_event(event: Any): ...
   
   # 新版类型安全事件
   from aivk_qq.napcat.events import QQEvent
   def handle_event(event: QQEvent): ...
   ```

4. **异步任务规范**：
   ```python
   # 弃用方式
   from typing import Coroutine
   def create_task() -> Coroutine: ...
   
   # 推荐方式
   from aivk_qq.napcat.utils.types import Task
   def create_task() -> Task[str]: ...
   ```

## Pyright 类型检查解决方案（Pyright Type Checking Solutions）
### 1. 弃用Optional类型（Deprecating Optional Type）
```python
# 旧写法
from typing import Optional
def old_style(param: Optional[int]) -> Optional[str]:
    pass

# 新写法
def new_style(param: int | None) -> str | None:
    pass
```

### 2. 清理未使用导入（Cleaning Unused Imports）
```python
# 错误示例
from typing import AsyncGenerator, Union
from websockets import WebSocketServerProtocol

# 正确做法
# 移除未使用的导入项
from typing import Union  # 只保留实际使用的类型
```

### 3. 避免使用Any类型（Avoiding Any Type）
```python
# 不允许写法
from typing import Any
def risky_func(data: Any) -> Any:
    pass

# 类型安全写法
from typing import TypeVar
T = TypeVar('T')
def safe_func(data: T) -> T:
    return data
```

### 4. 类属性类型注解（Class Attribute Type Annotations）
```python
# 不规范写法
class Config:
    arbitrary_types_allowed = True

# 规范写法
class Config:
    arbitrary_types_allowed: bool = True
```

## 日志级别类型约束（Log Level Type Constraints）
```python
# 不安全写法
from typing import Literal

def set_log_level(level: str):
    pass

# 类型安全写法
LogLevel = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

def set_log_level(level: LogLevel):
    pass
