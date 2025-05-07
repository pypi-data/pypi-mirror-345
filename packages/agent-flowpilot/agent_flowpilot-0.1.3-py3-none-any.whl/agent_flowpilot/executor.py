from typing import Dict, Any
from abc import ABC, abstractmethod
from .models import TaskResult, TaskStatus

class ToolExecutor(ABC):
    """工具执行器抽象类"""

    @abstractmethod
    async def execute(self, tool_name: str, parameters: Dict[str, Any]) -> TaskResult:
        """
        执行工具并返回结果
        return: TaskResult
        """
        pass

