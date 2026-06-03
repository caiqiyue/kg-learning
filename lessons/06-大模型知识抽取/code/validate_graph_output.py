"""校验 LLM 抽取结果，过滤不符合 schema 的节点和关系。"""

# 允许的节点类型。
ALLOWED_NODE_TYPES = {"Project", "Library", "DocumentType"}

# 允许的关系签名。
ALLOWED_RELATIONSHIPS = {
    ("Project", "USES", "Library"),
    ("Project", "EXTRACTS_FROM", "DocumentType"),
}

# 模拟 LLM 输出；其中包含一个不允许的关系 WRITES_TO。
llm_output = {
    "nodes": [
        {"id": "Neo4j LLM Graph Builder", "type": "Project"},
        {"id": "LangChain", "type": "Library"},
        {"id": "PDF", "type": "DocumentType"},
        {"id": "Neo4j", "type": "Database"},
    ],
    "relationships": [
        {"source": "Neo4j LLM Graph Builder", "source_type": "Project", "type": "USES", "target": "LangChain", "target_type": "Library"},
        {"source": "Neo4j LLM Graph Builder", "source_type": "Project", "type": "EXTRACTS_FROM", "target": "PDF", "target_type": "DocumentType"},
        {"source": "Neo4j LLM Graph Builder", "source_type": "Project", "type": "WRITES_TO", "target": "Neo4j", "target_type": "Database"},
    ],
}


def filter_nodes(nodes: list[dict]) -> list[dict]:
    """只保留类型在 schema 中的节点。"""
    return [node for node in nodes if node["type"] in ALLOWED_NODE_TYPES]


def filter_relationships(relationships: list[dict]) -> list[dict]:
    """只保留 schema 允许的关系签名。"""
    valid_relationships = []
    for relationship in relationships:
        signature = (
            relationship["source_type"],
            relationship["type"],
            relationship["target_type"],
        )
        if signature in ALLOWED_RELATIONSHIPS:
            valid_relationships.append(relationship)
    return valid_relationships


clean_nodes = filter_nodes(llm_output["nodes"])
clean_relationships = filter_relationships(llm_output["relationships"])

print("过滤后的节点:", clean_nodes)
print("过滤后的关系:", clean_relationships)
