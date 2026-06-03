"""模拟一个 LLM 知识抽取协议，不实际调用模型。"""

chunk_text = "Neo4j LLM Graph Builder uses LangChain to extract entities and relationships from documents."

schema = {
    "allowed_nodes": ["Project", "Library", "Database", "Document"],
    "allowed_relationships": [
        ("Project", "USES", "Library"),
        ("Project", "STORES_IN", "Database"),
        ("Project", "EXTRACTS_FROM", "Document"),
    ],
}

prompt = f"""
你是知识图谱抽取器。
只允许使用这些节点类型: {schema["allowed_nodes"]}
只允许使用这些关系三元组: {schema["allowed_relationships"]}
从文本中抽取事实，不要补充文本没有说的信息。
文本: {chunk_text}
输出 JSON，包含 nodes 和 relationships。
"""

mock_llm_output = {
    "nodes": [
        {"id": "Neo4j LLM Graph Builder", "type": "Project"},
        {"id": "LangChain", "type": "Library"},
        {"id": "documents", "type": "Document"},
    ],
    "relationships": [
        {"source": "Neo4j LLM Graph Builder", "type": "USES", "target": "LangChain"},
        {"source": "Neo4j LLM Graph Builder", "type": "EXTRACTS_FROM", "target": "documents"},
    ],
}

print(prompt)
print(mock_llm_output)
