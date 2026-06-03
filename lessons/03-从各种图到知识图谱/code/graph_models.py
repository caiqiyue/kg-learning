"""用最小 Python 结构理解普通图、属性图和知识图谱。"""

# 普通图：只保存连接关系，适合讲路径和连通性。
simple_graph = {
    "A": ["B", "C"],
    "B": ["C"],
    "C": []
}

# 属性图：节点和边都有类型与属性，更接近 Neo4j 的数据模型。
property_graph = {
    "nodes": [
        {"id": "neo4j", "labels": ["Database"], "properties": {"name": "Neo4j"}},
        {"id": "cypher", "labels": ["QueryLanguage"], "properties": {"name": "Cypher"}}
    ],
    "relationships": [
        {
            "start": "neo4j",
            "type": "SUPPORTS",
            "end": "cypher",
            "properties": {"reason": "graph pattern query"}
        }
    ]
}

# 知识图谱：在属性图基础上强调语义、来源和可查询事实。
knowledge_graph_fact = {
    "subject": "llm-graph-builder",
    "predicate": "USES",
    "object": "Neo4j",
    "source": "project README",
    "confidence": 0.95
}

print("普通图:", simple_graph)
print("属性图:", property_graph)
print("知识图谱事实:", knowledge_graph_fact)
