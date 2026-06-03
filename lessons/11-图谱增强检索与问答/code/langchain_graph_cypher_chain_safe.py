"""LangChain GraphCypherQAChain 安全使用示例。

Text2Cypher 很有价值，但生产环境必须加安全边界：
1. 使用只读 Neo4j 账号。
2. 限制暴露给 LLM 的 schema。
3. 执行前校验 Cypher，禁止写入、删除、无限路径。
4. 对返回行数做 LIMIT。
"""

import os
import re
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI


BLOCKED_KEYWORDS = {
    "CREATE", "MERGE", "DELETE", "DETACH", "SET", "REMOVE", "DROP", "CALL", "LOAD", "FOREACH"
}


def validate_readonly_cypher(cypher: str) -> None:
    """执行前校验 Cypher，防止 LLM 生成危险语句。"""
    normalized = re.sub(r"\s+", " ", cypher.upper())
    for keyword in BLOCKED_KEYWORDS:
        if re.search(rf"\b{keyword}\b", normalized):
            raise ValueError(f"禁止执行包含 {keyword} 的 Cypher")
    if "[*" in normalized and ".." not in normalized:
        raise ValueError("禁止无限长度路径查询")
    if " LIMIT " not in normalized:
        raise ValueError("生产查询必须包含 LIMIT")


graph = Neo4jGraph(
    url=os.environ.get("NEO4J_URI", "neo4j://localhost:7687"),
    username=os.environ.get("NEO4J_READONLY_USERNAME", "neo4j"),
    password=os.environ.get("NEO4J_READONLY_PASSWORD", "password"),
    enhanced_schema=True,
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=False,
)

question = "转化率下降可能由哪些原因导致？只返回 10 条。"

# 真实系统可把 chain 拆成“生成 Cypher -> 校验 -> 执行 -> 汇总回答”四步。
generated_cypher = """
MATCH (:Metric {id: 'conversion_rate'})-[:INDICATES]->(s:Symptom)-[:MAY_BE_CAUSED_BY]->(c:Cause)
RETURN s.name AS symptom, c.name AS cause
LIMIT 10
"""
validate_readonly_cypher(generated_cypher)

print("Cypher 通过安全校验，可以执行:")
print(generated_cypher)
