"""一个给 Agent 使用的图谱查询工具协议示例。"""

from dataclasses import dataclass


@dataclass
class GraphQueryRequest:
    entity_id: str
    max_hops: int = 2
    include_sources: bool = True


def build_neighborhood_query(request: GraphQueryRequest) -> tuple[str, dict]:
    """只生成受控查询模板，避免 Agent 直接拼任意 Cypher。"""
    max_hops = min(max(request.max_hops, 1), 3)
    cypher = f"""
    MATCH (e {{id: $entity_id}})
    OPTIONAL MATCH path = (e)-[*1..{max_hops}]-(neighbor)
    OPTIONAL MATCH (chunk:Chunk)-[:HAS_ENTITY]->(e)
    OPTIONAL MATCH (chunk)-[:PART_OF]->(doc:Document)
    RETURN e, collect(DISTINCT path) AS paths,
           collect(DISTINCT doc.fileName) AS sources
    """
    return cypher, {"entity_id": request.entity_id}


request = GraphQueryRequest(entity_id="Neo4j", max_hops=2)
query, params = build_neighborhood_query(request)
print(query)
print(params)
