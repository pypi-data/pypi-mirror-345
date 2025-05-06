from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Awaitable
from abc import ABC, abstractmethod
from .models import ResultMessage

class MessageAdapter(ABC):
    """外部服务适配器抽象类"""

    @abstractmethod
    async def request_user_input(
        self, task_id: str, question: str, params: List[str]
    ) -> Dict[str, Any]:
        """通过外部服务请求用户输入"""
        pass

    @abstractmethod
    async def check_response(self, task_id: str) -> Optional[Dict[str, Any]]:
        """检查是否有用户响应"""
        pass

    @abstractmethod
    async def finished_notify(self, message: ResultMessage):
        pass
