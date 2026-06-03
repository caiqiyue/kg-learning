"""把简单三元组转换为 Cypher MERGE 语句。"""

triples = [
    ("Neo4j", "SUPPORTS", "Cypher"),
    ("GraphRAG", "USES", "KnowledgeGraph"),
    ("Chunk", "HAS_ENTITY", "Entity"),
]


def normalize_relationship(predicate: str) -> str:
    """关系类型在 Neo4j 中通常使用大写和下划线，便于统一查询。"""
    return predicate.strip().upper().replace(" ", "_")


for subject, predicate, obj in triples:
    rel_type = normalize_relationship(predicate)
    # MERGE 用于幂等写入：存在就复用，不存在就创建。
    cypher = (
        "MERGE (s:Entity {id: $subject})\n"
        "MERGE (o:Entity {id: $object})\n"
        f"MERGE (s)-[:{rel_type}]->(o);"
    )
    print("--", (subject, predicate, obj))
    print(cypher)
    print({"subject": subject, "object": obj})
