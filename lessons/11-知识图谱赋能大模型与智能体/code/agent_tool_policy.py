"""Agent 图谱工具安全策略示例。"""

POLICY = {
    "allowed_operations": ["read_entity", "read_neighborhood", "read_sources"],
    "blocked_cypher_keywords": ["DELETE", "DETACH", "DROP", "CREATE", "MERGE", "SET"],
    "max_hops": 3,
    "max_records": 50,
    "require_sources": True,
}


def validate_tool_call(operation: str, max_hops: int, requested_records: int) -> list[str]:
    """校验 Agent 工具调用是否符合企业安全策略。"""
    errors = []
    # 只允许白名单操作，避免 Agent 调用未审核能力。
    if operation not in POLICY["allowed_operations"]:
        errors.append("操作不在白名单中")
    # 多跳太大容易导致路径爆炸，也可能带出无关或越权上下文。
    if max_hops > POLICY["max_hops"]:
        errors.append("多跳范围过大，可能造成路径爆炸")
    # 返回太多记录会增加 token 成本，也会提高敏感信息暴露风险。
    if requested_records > POLICY["max_records"]:
        errors.append("返回记录数过大，可能泄露过多上下文")
    return errors


print(validate_tool_call("read_neighborhood", max_hops=2, requested_records=20))
print(validate_tool_call("delete_entity", max_hops=5, requested_records=500))
