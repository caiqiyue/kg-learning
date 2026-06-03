"""LangChain GraphCypherQAChain 示例。

运行前安装:
    pip install langchain-openai langchain-neo4j

环境变量:
    export OPENAI_API_KEY='你的 key'
    export NEO4J_URI='neo4j://localhost:7687'
    export NEO4J_USERNAME='neo4j'
    export NEO4J_PASSWORD='password'

注意：
GraphCypherQAChain 很适合教学 Text-to-Cypher，但生产系统必须限制 schema、
只读权限和危险语句。本课程同时提供 graph_cypher_qa_demo.py 的白名单模板版本。
"""

from __future__ import annotations

import os

from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI


NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")


def build_chain() -> GraphCypherQAChain:
    """创建只用于查询演示的 GraphCypherQAChain。"""
    graph = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        include_types=["Document", "Chunk", "__Entity__", "HAS_ENTITY", "PART_OF"],
    )
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        verbose=True,
        # LangChain 要求显式声明允许危险请求。
        # 这里仍然建议用只读 Neo4j 账号运行，并在生产中增加 Cypher 审核层。
        allow_dangerous_requests=True,
    )


def main() -> None:
    chain = build_chain()
    response = chain.invoke(
        {
            "query": "demo.pdf 这个文档中抽取出了哪些实体？请按 chunk 位置排序。"
        }
    )
    print(response["result"])


if __name__ == "__main__":
    main()
