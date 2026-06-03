"""Neo4j Driver 版局部 GraphRAG 检索。

运行前安装:
    pip install neo4j

环境变量:
    export NEO4J_URI='neo4j://localhost:7687'
    export NEO4J_USERNAME='neo4j'
    export NEO4J_PASSWORD='password'

这个示例假设数据库中已有：
- (:Chunk {id, text, embedding}) 节点。
- (:Chunk)-[:HAS_ENTITY]->(:__Entity__ {id}) 溯源关系。
- 实体之间的业务关系，例如 (:__Entity__)-[:USES]->(:__Entity__)。
- 名为 chunk_embedding_vector 的 Neo4j 向量索引。
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from neo4j import GraphDatabase, Transaction


NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")


@dataclass(frozen=True)
class LocalContext:
    """一次局部 GraphRAG 命中的上下文块。"""

    chunk_id: str
    text: str
    score: float
    entities: list[str]
    facts: list[str]


def query_local_context(tx: Transaction, embedding: list[float], top_k: int = 5) -> list[LocalContext]:
    """先查向量索引，再沿命中 chunk 的实体扩展一跳邻域。"""
    result = tx.run(
        """
        CALL db.index.vector.queryNodes('chunk_embedding_vector', $top_k, $embedding)
        YIELD node AS chunk, score
        OPTIONAL MATCH (chunk)-[:HAS_ENTITY]->(entity:__Entity__)
        OPTIONAL MATCH (entity)-[rel]-(neighbor:__Entity__)
        WHERE type(rel) IN ['USES', 'SUPPORTS', 'MENTIONS', 'STORES_IN', 'EXTRACTS_FROM']
        RETURN chunk.id AS chunkId,
               chunk.text AS text,
               score,
               collect(DISTINCT entity.id) AS entities,
               collect(DISTINCT entity.id + ' - ' + type(rel) + ' - ' + neighbor.id)[0..12] AS facts
        ORDER BY score DESC
        """,
        embedding=embedding,
        top_k=top_k,
    )
    return [
        LocalContext(
            chunk_id=record["chunkId"],
            text=record["text"],
            score=record["score"],
            entities=record["entities"],
            facts=[fact for fact in record["facts"] if fact],
        )
        for record in result
    ]


def build_prompt_context(contexts: list[LocalContext]) -> str:
    """把 Neo4j 查询结果转成可交给 LLM 的上下文。"""
    blocks = []
    for context in contexts:
        blocks.append(
            "\n".join(
                [
                    f"chunk_id: {context.chunk_id}",
                    f"score: {context.score:.4f}",
                    f"text: {context.text}",
                    f"entities: {', '.join(context.entities)}",
                    "facts:",
                    *[f"- {fact}" for fact in context.facts],
                ]
            )
        )
    return "\n\n".join(blocks)


def main() -> None:
    # 教学占位：真实项目应调用 embedding 模型生成和索引维度一致的向量。
    fake_embedding = [0.0] * 1536
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            contexts = session.execute_read(query_local_context, fake_embedding, 3)
            print(build_prompt_context(contexts))
    finally:
        driver.close()


if __name__ == "__main__":
    main()
