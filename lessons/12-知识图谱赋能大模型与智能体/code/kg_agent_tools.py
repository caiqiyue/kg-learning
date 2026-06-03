"""知识图谱 Agent 工具示例：受控查询、参数校验、结果裁剪。"""

from dataclasses import dataclass


@dataclass
class ToolResult:
    content: str
    sources: list[str]


def reject_dangerous_text(value: str) -> None:
    """拒绝明显危险的输入，降低 Cypher 注入和误删风险。"""
    # Agent 的自然语言输入可能被恶意构造成 Cypher 片段，所以先做关键词拦截。
    dangerous_keywords = ["DELETE", "DETACH", "DROP", "CREATE", "MERGE", "SET", ";"]
    upper_value = value.upper()
    if any(keyword in upper_value for keyword in dangerous_keywords):
        raise ValueError("输入包含危险 Cypher 片段，已拒绝")


def build_entity_lookup_query(entity_id: str) -> tuple[str, dict]:
    """构建只读实体查询；查询文本固定，参数单独传入。"""
    # 先校验参数，再进入查询模板。
    reject_dangerous_text(entity_id)
    # 查询模板固定，只允许读取实体、标签和来源，不允许 Agent 自由拼 Cypher。
    cypher = """
    MATCH (e:__Entity__ {id: $entity_id})
    OPTIONAL MATCH (chunk:Chunk)-[:HAS_ENTITY]->(e)
    OPTIONAL MATCH (chunk)-[:PART_OF]->(doc:Document)
    RETURN e.id AS entity,
           labels(e) AS labels,
           collect(DISTINCT doc.fileName)[0..5] AS sources
    LIMIT 1
    """
    return cypher, {"entity_id": entity_id}


def format_tool_result(record: dict) -> ToolResult:
    """把数据库结果裁剪为 Agent 可消费的短文本。"""
    # 返回来源列表，方便 Agent 在最终回答中说明证据来自哪里。
    sources = record.get("sources", [])
    # 结果文本保持短小，避免把过多数据库上下文塞给模型。
    content = f"实体 {record.get('entity')} 的标签是 {record.get('labels')}。来源包括: {sources}"
    return ToolResult(content=content, sources=sources)


query, params = build_entity_lookup_query("Neo4j")
print(query)
print(params)
