from agent_flowpilot.tools import *

def test_tools():
    def sum_func(a, b):
            return a + b
    toolbox = ToolBox()
    toolbox.register("sum_tool", sum_func, "计算两个数的和")
    print(toolbox.dump())
    print(toolbox.to_function_calling())
    print(toolbox.to_schema())
