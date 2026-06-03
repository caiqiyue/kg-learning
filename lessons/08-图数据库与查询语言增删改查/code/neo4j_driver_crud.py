"""Python + Neo4j Driver CRUD 示例。

运行前需要安装:
    pip install neo4j

并设置环境变量:
    export NEO4J_URI='neo4j://localhost:7687'
    export NEO4J_USERNAME='neo4j'
    export NEO4J_PASSWORD='password'
"""

import os
from neo4j import GraphDatabase


# 从环境变量读取连接信息，避免把数据库密码写死在代码里。
NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")


def create_driver():
    """创建 Neo4j driver；driver 是线程安全的，真实项目通常全局复用。"""
    return GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
    )


def upsert_document(tx, file_name: str, source_url: str) -> None:
    """幂等创建或更新 Document 节点。"""
    tx.run(
        """
        MERGE (d:Document {fileName: $file_name})
        SET d.url = $source_url,
            d.status = 'New',
            d.updatedAt = datetime()
        """,
        file_name=file_name,
        source_url=source_url,
    )


def upsert_chunk(tx, file_name: str, chunk_id: str, text: str, position: int) -> None:
    """创建 Chunk，并建立 Chunk 到 Document 的溯源关系。"""
    tx.run(
        """
        MATCH (d:Document {fileName: $file_name})
        MERGE (c:Chunk {id: $chunk_id})
        SET c.text = $text,
            c.position = $position,
            c.updatedAt = datetime()
        MERGE (c)-[:PART_OF]->(d)
        """,
        file_name=file_name,
        chunk_id=chunk_id,
        text=text,
        position=position,
    )


def upsert_entity_and_source(tx, chunk_id: str, entity_id: str, label: str) -> None:
    """创建实体，并用 HAS_ENTITY 记录它来自哪个 chunk。"""
    tx.run(
        """
        MATCH (c:Chunk {id: $chunk_id})
        CALL apoc.merge.node(['__Entity__', $label], {id: $entity_id}) YIELD node AS e
        MERGE (c)-[:HAS_ENTITY]->(e)
        """,
        chunk_id=chunk_id,
        entity_id=entity_id,
        label=label,
    )


def read_entities_for_document(tx, file_name: str) -> list[dict]:
    """查询某个文档抽取出的实体，并返回来源 chunk 位置。"""
    result = tx.run(
        """
        MATCH (d:Document {fileName: $file_name})<-[:PART_OF]-(c:Chunk)-[:HAS_ENTITY]->(e)
        RETURN e.id AS entity_id,
               labels(e) AS labels,
               c.position AS chunk_position
        ORDER BY c.position, entity_id
        """,
        file_name=file_name,
    )
    return [record.data() for record in result]


def safe_delete_document_only(tx, file_name: str) -> None:
    """删除 Document 和 Chunk，但保留可能被其他文档共享的 Entity。"""
    tx.run(
        """
        MATCH (d:Document {fileName: $file_name})
        OPTIONAL MATCH (d)<-[:PART_OF]-(c:Chunk)
        DETACH DELETE c, d
        """,
        file_name=file_name,
    )


def main() -> None:
    """演示一次完整 CRUD：写入、查询、删除。"""
    driver = create_driver()
    try:
        with driver.session() as session:
            session.execute_write(upsert_document, "demo.pdf", "file:///demo.pdf")
            session.execute_write(upsert_chunk, "demo.pdf", "chunk-001", "Neo4j uses Cypher.", 1)
            session.execute_write(upsert_entity_and_source, "chunk-001", "Neo4j", "Database")
            entities = session.execute_read(read_entities_for_document, "demo.pdf")
            print("文档实体:", entities)
            session.execute_write(safe_delete_document_only, "demo.pdf")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
