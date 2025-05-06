# ========== 基础类型定义 ==========
from enum import Enum, auto
from typing import *
from dataclasses import dataclass

class TaskStatus(Enum):
    PENDING = auto()
    WAITING_FOR_INPUT = auto()
    READY = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class TaskDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]
    required_parameters: List[str]
    optional_parameters: List[str]
    execution_mode: str  # 'sequential', 'parallel'
    depends_on: List[str]  # 任务名称列表
    is_end_task: bool = False  # 是否是结束任务

@dataclass
class TaskResult:
    output: Dict[str, Any]
    error: Optional[str]
    status: TaskStatus
    exception: Optional[Exception] = None

    def __post_init__(self):
        """验证状态一致性"""
        if self.status == TaskStatus.COMPLETED and self.error:
            raise ValueError("Completed task cannot have error")
        if self.status == TaskStatus.FAILED and not self.error:
            raise ValueError("Failed task must have error message")


# ========== 异常定义 ==========
class TaskFailedError(Exception):
    """自定义任务失败异常"""

    def __init__(self, task_name: str, reason: str, dependency_chain: List[str] = None):
        self.task_name = task_name
        self.reason = reason
        self.dependency_chain = dependency_chain or []
        message = f"任务 '{task_name}' 失败: {reason}"
        if dependency_chain:
            message += f"\n依赖链: {' → '.join(dependency_chain)}"
        super().__init__(message)


# ========== 核心类实现 ==========
class Task:
    def __init__(self, definition: TaskDefinition):
        self.definition = definition
        self.status = TaskStatus.PENDING
        self.result: Optional[TaskResult] = None
        self._resolved_parameters = {}
        self._missing_parameters = []
        self.is_end_task = definition.is_end_task  # 新增：标记是否为结束任务

    def resolve_parameters(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        解析参数
        返回: (是否成功, 失败原因)
        """
        self._resolved_parameters = {}
        self._missing_parameters = []

        # 1. 合并默认参数
        for param, value in self.definition.parameters.items():
            if value is not None:
                self._resolved_parameters[param] = value

        # 2. 检查必需参数
        missing_required = []
        for param in self.definition.required_parameters:
            if param not in self._resolved_parameters or not self._resolved_parameters[param]:
                # 尝试从上下文获取
                if param in context and context[param]:
                    self._resolved_parameters[param] = context[param]
                else:
                    missing_required.append(param)

        # 3. 记录缺失参数
        self._missing_parameters = missing_required

        if missing_required:
            return False, f"Missing required parameters: {missing_required}"
        return True, ""

    @property
    def resolved_parameters(self) -> Dict[str, Any]:
        return self._resolved_parameters

    @property
    def missing_parameters(self) -> List[str]:
        return self._missing_parameters

    def mark_ready(self):
        self.status = TaskStatus.READY

    def mark_running(self):
        self.status = TaskStatus.RUNNING

    def mark_completed(self, result: TaskResult):
        self.result = result
        self.status = TaskStatus.COMPLETED

    def mark_failed(self, error: str, exception: Exception = None):
        self.result = TaskResult(
            output={}, error=error, status=TaskStatus.FAILED, exception=exception
        )
        self.status = TaskStatus.FAILED

    def mark_skipped(self, reason: str):
        self.result = TaskResult(output={}, error=reason, status=TaskStatus.SKIPPED)
        self.status = TaskStatus.SKIPPED

    def __repr__(self):
        return f"<Task name={self.definition.name} status={self.status} depends_on={self.definition.depends_on} is_end_task={self.is_end_task}>"


@dataclass
class ResultMessage:
    status: TaskStatus
    output: Dict[str, Any]
    error: Optional[str] = None
    exception: Optional[Exception] = None

    def __repr__(self):
        return f"<ResultMessage status={self.status} error={self.error} output={self.output}>"
