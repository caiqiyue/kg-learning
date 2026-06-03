"""Neo4j GraphRAG Python 包使用示例。

运行前参考官方文档安装:
    pip install "neo4j-graphrag[openai]"

说明：
neo4j-graphrag 是 Neo4j 官方 GraphRAG Python 包，
用于知识图谱构建、向量检索、图检索和 GraphRAG 管道。
这个文件保留为教学模板，具体类名和参数请以当前官方文档为准。
"""

import os
import neo4j


NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")


def create_driver():
    """创建 Neo4j 官方 driver，供 GraphRAG pipeline 复用。"""
    return neo4j.GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
    )


def build_pipeline_config() -> dict:
    """用普通字典表达 GraphRAG pipeline 的关键配置，便于理解。"""
    return {
        "schema": {
            "node_types": ["Metric", "Symptom", "Cause", "Action", "Evidence"],
            "relationship_types": [
                "INDICATES",
                "MAY_BE_CAUSED_BY",
                "RECOMMENDS",
                "SUPPORTED_BY",
            ],
        },
        "indexes": {
            "chunk_vector": {"label": "Chunk", "property": "embedding", "dimensions": 1536},
            "entity_vector": {"label": "__Entity__", "property": "embedding", "dimensions": 1536},
        },
        "retrieval": {
            "local_search": "从实体邻域扩展证据",
            "global_search": "从社区摘要回答全局问题",
            "hybrid_search": "组合向量、全文、图路径",
        },
    }


if __name__ == "__main__":
    driver = create_driver()
    try:
        print("GraphRAG pipeline 教学配置:")
        print(build_pipeline_config())
    finally:
        driver.close()
