"""LangChain GraphDocument 写入 Neo4j 示例。

运行前需要安装:
    pip install langchain-neo4j langchain-core

并设置:
    export NEO4J_URI='neo4j://localhost:7687'
    export NEO4J_USERNAME='neo4j'
    export NEO4J_PASSWORD='password'

说明：
LLMGraphTransformer 抽取出的 GraphDocument 可以交给 Neo4jGraph 写入。
真实系统写入前仍要做 schema 校验、实体规范化和人工审核。
"""

import os
from langchain_core.documents import Document
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_neo4j import Neo4jGraph


graph = Neo4jGraph(
    url=os.environ.get("NEO4J_URI", "neo4j://localhost:7687"),
    username=os.environ.get("NEO4J_USERNAME", "neo4j"),
    password=os.environ.get("NEO4J_PASSWORD", "password"),
)

source_document = Document(
    page_content="转化率下降可能与线索质量偏低有关。",
    metadata={"source": "sales-diagnosis-playbook.md", "chunk_id": "chunk-001"},
)

metric = Node(id="conversion_rate", type="Metric", properties={"name": "转化率"})
cause = Node(id="low_lead_quality", type="Cause", properties={"name": "线索质量偏低"})

relationship = Relationship(
    source=metric,
    target=cause,
    type="MAY_BE_CAUSED_BY",
    properties={"confidence": 0.86},
)

graph_document = GraphDocument(
    nodes=[metric, cause],
    relationships=[relationship],
    source=source_document,
)

# include_source=True 会把来源文档也写入图谱，方便后续做引用和审计。
graph.add_graph_documents([graph_document], include_source=True)
print("GraphDocument 已写入 Neo4j")
