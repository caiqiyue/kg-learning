"""LangChain + Neo4j 图谱抽取示例。

运行前需要安装:
    pip install langchain-openai langchain-experimental langchain-core

并设置:
    export OPENAI_API_KEY='你的 key'

这个示例展示 LLMGraphTransformer 的核心用法。
"""

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer


# 准备一个 Document；真实项目里它通常来自 PDF loader 或网页 loader。
documents = [
    Document(
        page_content="Neo4j LLM Graph Builder uses LangChain to extract entities from PDF documents."
    )
]

# 创建 LLM；temperature=0 可以减少抽取结果的随机性。
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 限制允许的节点类型，避免模型随意创造 label。
allowed_nodes = ["Project", "Library", "DocumentType"]

# 限制允许的关系三元组，避免关系名称漂移。
allowed_relationships = [
    ("Project", "USES", "Library"),
    ("Project", "EXTRACTS_FROM", "DocumentType"),
]

# 创建图转换器；strict_mode=True 表示尽量只保留 schema 允许的输出。
transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=allowed_nodes,
    allowed_relationships=allowed_relationships,
    strict_mode=True,
    node_properties=["description"],
    relationship_properties=["description"],
)

# 把文本转换为 GraphDocument。
# GraphDocument 里包含 nodes 和 relationships，后续可写入 Neo4j。
graph_documents = transformer.convert_to_graph_documents(documents)

# 打印抽取结果，方便人工审核。
for graph_document in graph_documents:
    print("节点:")
    for node in graph_document.nodes:
        print(node)
    print("关系:")
    for relationship in graph_document.relationships:
        print(relationship)
