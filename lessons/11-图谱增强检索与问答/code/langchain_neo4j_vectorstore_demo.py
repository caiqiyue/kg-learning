"""LangChain + Neo4jVector 示例：把 Neo4j 当向量库使用。

运行前需要安装:
    pip install langchain-neo4j langchain-openai

并设置:
    export OPENAI_API_KEY='你的 key'
    export NEO4J_URI='neo4j://localhost:7687'
    export NEO4J_USERNAME='neo4j'
    export NEO4J_PASSWORD='password'
"""

import os
from langchain_neo4j import Neo4jVector
from langchain_openai import OpenAIEmbeddings


embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vector_store = Neo4jVector.from_existing_index(
    embedding=embeddings,
    url=os.environ.get("NEO4J_URI", "neo4j://localhost:7687"),
    username=os.environ.get("NEO4J_USERNAME", "neo4j"),
    password=os.environ.get("NEO4J_PASSWORD", "password"),
    index_name="chunk_vector",
    node_label="Chunk",
    text_node_property="text",
    embedding_node_property="embedding",
)

docs = vector_store.similarity_search(
    "销售转化率下降应该优先诊断哪些原因？",
    k=5,
)

for doc in docs:
    print("文本:", doc.page_content)
    print("元数据:", doc.metadata)
