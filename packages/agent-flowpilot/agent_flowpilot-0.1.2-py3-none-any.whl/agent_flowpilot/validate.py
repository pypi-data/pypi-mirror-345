def validate_tool_chain_output(data):
    """
    验证工具链输出的结构和参数。

    参数:
        data (dict): 待验证的输出数据

    返回:
        tuple: (is_valid: bool, 错误信息: str)
    """
    # Check basic structure
    if not isinstance(data, dict):
        return False, "输入必须是一个字典"

    # Check required top-level fields
    required_fields = ["tool_chain", "task_sequence", "follow_up"]
    for field in required_fields:
        if field not in data:
            return False, f"缺少必需字段: {field}"

    # Check tool_chain is a non-empty list
    if not isinstance(data["tool_chain"], list) or len(data["tool_chain"]) == 0:
        return False, "tool_chain 必须是一个非空列表"

    # Get first tool
    first_tool = data["tool_chain"][0]

    # Check first tool structure
    tool_required_fields = [
        "name",
        "description",
        "parameters",
        "required_parameters",
        "optional_parameters",
        "execution_mode",
        "depends_on",
    ]
    for field in tool_required_fields:
        if field not in first_tool:
            return False, f"缺少必需的工具字段: {field}"

    # Check parameters validation
    required_params = first_tool["required_parameters"]
    parameters = first_tool["parameters"]

    # Case 1: If required_parameters has values
    if required_params:
        # Check all required params exist in parameters
        missing_params = [p for p in required_params if p not in parameters]
        if missing_params:
            # If parameters are missing, check if we can proceed without them
            if not data["follow_up"]:
                return (
                    False,
                    f"缺少必需参数: {missing_params}，但 follow_up 不存在",
                )
            return False, "缺少必需参数，但标记为无需询问"

    # Case 2: If no required parameters, always valid
    return True, "验证通过"

if __name__ == '__main__':
    # Test cases
    test_data = {
        "tool_chain": [
            {
                "name": "start_vm",
                "description": "启动虚拟机",
                "parameters": {"vmid": 123},
                "required_parameters": ["vmid"],
                "optional_parameters": [],
                "execution_mode": "sequential",
                "depends_on": [],
            }
        ],
        "task_sequence": "直接调用 start_vm 启动指定ID的虚拟机。",
        "follow_up": [],
    }

    print(
        validate_tool_chain_output(test_data)
    )  # Should return (True, "验证通过")

    # Test missing required parameter
    test_data2 = {
        "tool_chain": [
            {
                "name": "start_vm",
                "description": "启动虚拟机",
                "parameters": {},
                "required_parameters": ["vmid"],
                "optional_parameters": [],
                "execution_mode": "sequential",
                "depends_on": [],
            }
        ],
        "task_sequence": "直接调用 start_vm 启动指定ID的虚拟机。",
        "follow_up": [],
    }

    print(
        validate_tool_chain_output(test_data2)
    )  # Should return (False, "缺少必需参数，但标记为无需询问")
