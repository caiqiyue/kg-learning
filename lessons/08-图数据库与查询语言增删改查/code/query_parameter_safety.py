"""Cypher 参数化与白名单示例。

重要原则：
- 节点属性值可以参数化，例如 e.id = $entity_id。
- label、relationship type、排序字段不能直接用参数替代。
- 如果必须动态选择 label 或关系类型，要使用白名单，而不是拼接任意用户输入。
"""

ALLOWED_RELATIONSHIPS = {
    "原因": "MAY_BE_CAUSED_BY",
    "推荐动作": "RECOMMENDS",
    "证据": "SUPPORTED_BY",
}


def build_safe_relationship_query(chinese_relation_name: str) -> str:
    """根据用户选择构造受控查询模板。"""
    relationship_type = ALLOWED_RELATIONSHIPS.get(chinese_relation_name)
    if relationship_type is None:
        raise ValueError(f"不允许查询这种关系: {chinese_relation_name}")

    # relationship_type 来自白名单，所以这里拼接是可控的。
    return f"""
    MATCH (source:__Entity__ {{id: $source_id}})-[:{relationship_type}]->(target:__Entity__)
    RETURN source.id AS sourceId, target.id AS targetId
    LIMIT $limit
    """


def unsafe_example(user_input: str) -> str:
    """反例：不要把用户输入直接拼进 Cypher。"""
    return f"MATCH (n {{id: '{user_input}'}}) RETURN n"


print(build_safe_relationship_query("原因"))
print("反例仅用于教学，不要执行:", unsafe_example("abc'}) DETACH DELETE n //"))
