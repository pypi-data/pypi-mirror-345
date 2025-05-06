
# FlowPilot

FlowPilot 是一个智能代理任务处理 SDK，具备以下核心功能：

- ✨ 意图识别
- 🛠️ 工具判断
- 📋 任务编排
- 🚀 任务执行

## 安装

### 通过 PyPI 安装

```bash
pip install flowpilot
```

### 通过源码安装

1. 克隆仓库：

```bash
git clone https://github.com/deepissue/flowpilot.git
cd flowpilot
```

2. 安装依赖：

```bash
pip install -e ".[test]"
```

这将以可编辑模式安装 `flowpilot` 包，并同时安装测试依赖。

## 结构说明

- `flowpilot.py`：统一流程入口，负责启动和管理任务执行流程。
- `intent.py`：意图识别器，基于输入的提示词进行意图分析，返回任务定义信息。
- `scheduler.py`：任务编排调度，负责任务的顺序和依赖关系管理。
- `executor.py`：任务执行器抽象类，具体任务执行逻辑的实现。
- `tools.py`：工具注解生成，提供辅助功能的工具接口。

## 使用示例

可以在 `test/demo.py` 中找到具体的使用示例。

```python
# 示例代码
from flowpilot import FlowPilot

flow = FlowPilot(...)
flow.load_task_definitions(task_definitions)
await flow.arun()
report = flow.get_execution_report()
print(report)
```

### 任务定义示例

任务定义是整个 SDK 的核心，结构如下：

```python
# 任务定义示例
task_definitions = [
    {
        "name": "create_vm",
        "description": "创建虚拟机",
        "parameters": {"vm_name": None},
        "required_parameters": [],
        "optional_parameters": ["vm_name"],
        "execution_mode": "sequential",
        "depends_on": [],
    }
]
```

## 测试

运行测试，可以使用以下命令：

```bash
pytest tests/
```

## 贡献

欢迎提交 PR 或 issue！任何问题或建议都可以提到 issue。

## License

MIT License
