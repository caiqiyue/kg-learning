"""Python + Neo4j Driver 事务批处理示例。

运行前需要安装:
    pip install neo4j

并设置环境变量:
    export NEO4J_URI='neo4j://localhost:7687'
    export NEO4J_USERNAME='neo4j'
    export NEO4J_PASSWORD='password'

这个例子重点展示三件事：
1. 用 execute_write 让 driver 自动处理可重试事务。
2. 用 UNWIND 批量写入，避免 Python 循环提交大量小事务。
3. 所有用户数据都通过参数传入，避免 Cypher 注入。
"""

import os
from neo4j import GraphDatabase


NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")


def create_driver():
    """创建 Neo4j driver；真实服务中通常在应用生命周期内复用。"""
    return GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
    )


def create_constraints(tx) -> None:
    """创建唯一约束，保证 MERGE 不会产生重复节点。"""
    tx.run("""
    CREATE CONSTRAINT document_file IF NOT EXISTS
    FOR (d:Document) REQUIRE d.fileName IS UNIQUE
    """)
    tx.run("""
    CREATE CONSTRAINT chunk_id IF NOT EXISTS
    FOR (c:Chunk) REQUIRE c.id IS UNIQUE
    """)
    tx.run("""
    CREATE CONSTRAINT entity_id IF NOT EXISTS
    FOR (e:__Entity__) REQUIRE e.id IS UNIQUE
    """)


def batch_upsert_chunks(tx, file_name: str, chunks: list[dict]) -> None:
    """批量写入 chunk，并建立 PART_OF 顺序关系。"""
    tx.run(
        """
        MERGE (d:Document {fileName: $fileName})
        SET d.updatedAt = datetime()
        WITH d
        UNWIND $chunks AS row
        MERGE (c:Chunk {id: row.id})
        SET c.text = row.text,
            c.position = row.position,
            c.updatedAt = datetime()
        MERGE (c)-[:PART_OF]->(d)
        WITH collect(c) AS orderedChunks
        UNWIND range(0, size(orderedChunks) - 2) AS index
        WITH orderedChunks[index] AS currentChunk,
             orderedChunks[index + 1] AS nextChunk
        MERGE (currentChunk)-[:NEXT_CHUNK]->(nextChunk)
        """,
        fileName=file_name,
        chunks=chunks,
    )


def batch_upsert_entities(tx, entities: list[dict], mentions: list[dict]) -> None:
    """批量写入实体，并建立 chunk 到实体的溯源关系。"""
    tx.run(
        """
        UNWIND $entities AS row
        MERGE (e:__Entity__ {id: row.id})
        SET e.name = row.name,
            e.type = row.type,
            e.updatedAt = datetime()
        """,
        entities=entities,
    )
    tx.run(
        """
        UNWIND $mentions AS row
        MATCH (c:Chunk {id: row.chunkId})
        MATCH (e:__Entity__ {id: row.entityId})
        MERGE (c)-[r:HAS_ENTITY]->(e)
        SET r.confidence = row.confidence
        """,
        mentions=mentions,
    )


def read_document_summary(tx, file_name: str) -> dict:
    """读取文档图谱摘要，作为 API 返回值或日志指标。"""
    result = tx.run(
        """
        MATCH (d:Document {fileName: $fileName})
        OPTIONAL MATCH (d)<-[:PART_OF]-(c:Chunk)
        OPTIONAL MATCH (c)-[:HAS_ENTITY]->(e:__Entity__)
        RETURN d.fileName AS fileName,
               count(DISTINCT c) AS chunkCount,
               count(DISTINCT e) AS entityCount
        """,
        fileName=file_name,
    )
    return result.single().data()


def main() -> None:
    """执行一个最小批处理写入流程。"""
    chunks = [
        {"id": "chunk-sales-001", "text": "转化率下降可能与线索质量有关。", "position": 1},
        {"id": "chunk-sales-002", "text": "销售跟进时效会影响成交率。", "position": 2},
    ]
    entities = [
        {"id": "conversion_rate", "name": "转化率", "type": "Metric"},
        {"id": "lead_quality", "name": "线索质量", "type": "Cause"},
        {"id": "follow_up_speed", "name": "跟进时效", "type": "Cause"},
    ]
    mentions = [
        {"chunkId": "chunk-sales-001", "entityId": "conversion_rate", "confidence": 0.95},
        {"chunkId": "chunk-sales-001", "entityId": "lead_quality", "confidence": 0.91},
        {"chunkId": "chunk-sales-002", "entityId": "follow_up_speed", "confidence": 0.9},
    ]

    driver = create_driver()
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            session.execute_write(create_constraints)
            session.execute_write(batch_upsert_chunks, "sales-diagnosis.md", chunks)
            session.execute_write(batch_upsert_entities, entities, mentions)
            summary = session.execute_read(read_document_summary, "sales-diagnosis.md")
            print("文档图谱摘要:", summary)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
