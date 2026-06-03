"""Text-to-Cypher / Graph QA 示例。

这个文件不直接调用 LLM，而是展示企业系统中应如何限制 Cypher 模板。
"""

SAFE_QUERY_TEMPLATES = {
    "count_documents": {
        "description": "统计 Document 节点数量",
        "cypher": "MATCH (d:Document) RETURN count(d) AS documentCount",
        "write": False,
    },
    "entity_neighborhood": {
        "description": "查询实体 1 到 2 跳邻域",
        "cypher": """
        MATCH (e:__Entity__ {id: $entity_id})
        OPTIONAL MATCH path = (e)-[*1..2]-(:__Entity__)
        RETURN e.id AS entity, collect(path) AS paths
        LIMIT 20
        """,
        "write": False,
    },
}


def get_safe_query(template_name: str, params: dict | None = None) -> tuple[str, dict]:
    """只允许从白名单模板中取查询，避免 LLM 生成危险 Cypher。"""
    # 如果模板不在白名单里，直接拒绝，避免模型自由生成删除或写入语句。
    if template_name not in SAFE_QUERY_TEMPLATES:
        raise ValueError(f"不允许的查询模板: {template_name}")
    template = SAFE_QUERY_TEMPLATES[template_name]
    # 问答工具默认只读；写入类操作应走单独审批流程。
    if template["write"]:
        raise ValueError("当前问答工具只允许只读查询")
    # 参数单独返回，执行时交给 driver 参数化传入，避免字符串拼接注入。
    return template["cypher"], params or {}


query, query_params = get_safe_query("entity_neighborhood", {"entity_id": "Neo4j"})
print(query)
print(query_params)
