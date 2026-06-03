"""Schema 驱动的 LLM 抽取后处理流水线。

这个脚本不调用真实 LLM，而是把“模型输出之后必须做什么”讲完整：
1. 规范化实体 id，减少同一实体的多种写法。
2. 校验节点类型和关系签名。
3. 过滤缺失端点、越界关系、空 id。
4. 给节点和关系补充 chunk 来源，方便 GraphRAG 引用证据。
"""

from __future__ import annotations

from dataclasses import dataclass


ALLOWED_NODE_TYPES = {"Project", "Library", "Database", "DocumentType"}
ALLOWED_RELATIONSHIPS = {
    ("Project", "USES", "Library"),
    ("Project", "STORES_IN", "Database"),
    ("Project", "EXTRACTS_FROM", "DocumentType"),
}


@dataclass(frozen=True)
class CleanGraph:
    """校验后的图谱片段。"""

    nodes: list[dict]
    relationships: list[dict]
    rejected: list[dict]


def normalize_entity_id(raw_id: str) -> str:
    """规范化实体 id。

    真实项目可以接入别名字典、大小写规则、公司后缀清洗、中文繁简转换等。
    这里保持教学可读性，只做空白清洗和常见别名合并。
    """
    aliases = {
        "neo4j database": "Neo4j",
        "neo4j": "Neo4j",
        "langchain": "LangChain",
        "pdf document": "PDF",
        "pdf": "PDF",
    }
    cleaned = " ".join(raw_id.strip().split())
    return aliases.get(cleaned.lower(), cleaned)


def clean_graph_output(llm_output: dict, chunk_id: str) -> CleanGraph:
    """把模型输出转成可写入图数据库的干净结构。"""
    rejected: list[dict] = []
    nodes_by_id: dict[str, dict] = {}

    for node in llm_output.get("nodes", []):
        node_id = normalize_entity_id(node.get("id", ""))
        node_type = node.get("type", "")
        if not node_id:
            rejected.append({"reason": "节点 id 为空", "item": node})
            continue
        if node_type not in ALLOWED_NODE_TYPES:
            rejected.append({"reason": "节点类型不在白名单", "item": node})
            continue
        nodes_by_id[node_id] = {
            "id": node_id,
            "type": node_type,
            "source_chunk_id": chunk_id,
        }

    clean_relationships: list[dict] = []
    for relationship in llm_output.get("relationships", []):
        source_id = normalize_entity_id(relationship.get("source", ""))
        target_id = normalize_entity_id(relationship.get("target", ""))
        relation_type = relationship.get("type", "")

        source_node = nodes_by_id.get(source_id)
        target_node = nodes_by_id.get(target_id)
        if source_node is None or target_node is None:
            rejected.append({"reason": "关系端点节点不存在", "item": relationship})
            continue

        signature = (source_node["type"], relation_type, target_node["type"])
        if signature not in ALLOWED_RELATIONSHIPS:
            rejected.append({"reason": "关系签名不在白名单", "item": relationship})
            continue

        clean_relationships.append(
            {
                "source": source_id,
                "source_type": source_node["type"],
                "type": relation_type,
                "target": target_id,
                "target_type": target_node["type"],
                "source_chunk_id": chunk_id,
            }
        )

    return CleanGraph(
        nodes=list(nodes_by_id.values()),
        relationships=clean_relationships,
        rejected=rejected,
    )


if __name__ == "__main__":
    raw_output = {
        "nodes": [
            {"id": "知识图谱构建器", "type": "Project"},
            {"id": "langchain", "type": "Library"},
            {"id": "neo4j database", "type": "Database"},
            {"id": "PDF Document", "type": "DocumentType"},
            {"id": "未来计划", "type": "Speculation"},
        ],
        "relationships": [
            {"source": "知识图谱构建器", "type": "USES", "target": "LangChain"},
            {"source": "知识图谱构建器", "type": "STORES_IN", "target": "Neo4j"},
            {"source": "知识图谱构建器", "type": "EXTRACTS_FROM", "target": "PDF"},
            {"source": "LangChain", "type": "WRITES_TO", "target": "Neo4j"},
        ],
    }

    graph = clean_graph_output(raw_output, chunk_id="lesson06-c1")
    print("可写入节点:")
    for item in graph.nodes:
        print(item)
    print("\n可写入关系:")
    for item in graph.relationships:
        print(item)
    print("\n被拒绝项目:")
    for item in graph.rejected:
        print(item)
