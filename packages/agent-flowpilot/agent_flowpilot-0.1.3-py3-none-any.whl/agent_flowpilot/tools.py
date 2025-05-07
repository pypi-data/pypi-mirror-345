import inspect
import functools
from .function import func_to_function_calling

def _tool_params(func):
    sig = inspect.signature(func)
    return [
        name
        for name, param in sig.parameters.items()
        if name != "self" and param.default is param.empty
    ]

def _tool_info(func):
    params = _tool_params(func)
    params = ",".join(params)
    return {
        "name": func._tool_name,
        "func": f"{func.__name__}({params})",
        "description": func._tool_description,
    }

class ToolBox:
    """
    工具盒
    1. 使用方式1 初始化实例，调用register接口注册工具
        def sum_func(a, b):
            return a + b
        toolbox = ToolBox()
        toolbox.register("sum_tool", sum_func, "计算两个数的和")
    2. 使用方式2 装饰器方式注册工具
        class ExampleTool(ToolBox):
            def __init__(self):
                super().__init__()
                
            @ToolBox.tool(name="example_tool", description="这是一个示例工具")
            def example_method(self, arg1, arg2):
                return arg1 + arg2
        example_tool = ExampleTool()
        tools = example_tool.to_schema()
    """
    def __init__(self):
        self.tools = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if getattr(method, "_is_tool", False):
                tool_name = method._tool_name
                self.tools[tool_name] = method

    def get(self, name: str):
        """
        获取工具
        """
        return self.tools.get(name, None)
    
    def register(self, name: str, func, description: str = ""):
        """
        注册工具
        """
        if not callable(func):
            raise ValueError(f"Input <func> must be a callable function.")
        self.tools[name] = func
        func._is_tool = True
        func._tool_name = name
        func._tool_description = description or func.__doc__

    def dump(self):
        """
        导出工具列表
        """
        return [_tool_info(func) for name, func in self.tools.items()]
    
    def to_schema(self):
        """
        转换为简单的工具schema列表
        """
        return [_tool_info(func) for name, func in self.tools.items()]

    def to_function_calling(self):
        """
        转换为函数列表open ai 格式的function calling
        @https://platform.openai.com/docs/guides/function-calling?api-mode=responses
        """
        return [ func_to_function_calling(func) for name, func in self.tools.items() ]

    @classmethod
    def tool(cls, name: str = None, description: str = ""):
        """
        工具装饰器, 必须是一个继承了ToolBox的类的方法
        只标记，不立即注册
        """
        def decorator(func):
            func._is_tool = True
            func._tool_name = name or func.__name__
            func._tool_description = description or func.__doc__
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper

        return decorator
