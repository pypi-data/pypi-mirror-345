from agent_flowpilot.intent import IntentRecognizer
from agent_flowpilot.tools import ToolBox

class SimpleTool(ToolBox):
    def __init__(self):
        super().__init__()
    @ToolBox.tool(name="sum_tool", description="This is a sum tool")
    def sum_tool(self, arg1, arg2):
        return arg1 + arg2


def test_recognize():
    recognizer = IntentRecognizer()
    toolbox = SimpleTool()
    prompt = recognizer.prompt("create a vm", toolbox.to_function_calling(), context='', tips='我是一个vm助手')
    assert prompt.find("我是一个vm助手") != -1
    assert toolbox.get("sum_tool")(1, 2) == 3
