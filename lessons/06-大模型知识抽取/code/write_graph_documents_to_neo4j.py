"""把 LangChain GraphDocument 写入 Neo4j 的示例。

运行前安装:
    pip install neo4j langchain-core langchain-community

环境变量:
    export NEO4J_URI='neo4j://localhost:7687'
    export NEO4J_USERNAME='neo4j'
    export NEO4J_PASSWORD='password'

说明：
LLMGraphTransformer 可以产出 GraphDocument，但教学和生产都不应只停在打印结果。
这个脚本演示如何把抽取结果和 chunk 来源一起写进 Neo4j。
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from neo4j import GraphDatabase, Transaction


NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

# 动态关系类型必须限制在白名单中，不能把模型输出原样拼进 Cypher。
ALLOWED_RELATION_TYPES = {"USES", "STORES_IN", "EXTRACTS_FROM"}


@dataclass(frozen=True)
class ExtractedNode:
    """从 GraphDocument node 转出的教学结构。"""

    node_id: str
    node_type: str
    description: str = ""


@dataclass(frozen=True)
class ExtractedRelationship:
    """从 GraphDocument relationship 转出的教学结构。"""

    source_id: str
    relation_type: str
    target_id: str
    description: str = ""


def create_constraints(tx: Transaction) -> None:
    """GraphDocument 写库前先保证唯一键存在。"""
    tx.run(
        """
        CREATE CONSTRAINT document_file_name_unique IF NOT EXISTS
        FOR (d:Document)
        REQUIRE d.fileName IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS
        FOR (c:Chunk)
        REQUIRE c.id IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
        FOR (e:__Entity__)
        REQUIRE e.id IS UNIQUE
        """
    )


def write_chunk_and_nodes(
    tx: Transaction,
    file_name: str,
    chunk_id: str,
    chunk_text: str,
    nodes: list[ExtractedNode],
) -> None:
    """写入文档、chunk、实体节点和 HAS_ENTITY 溯源关系。"""
    tx.run(
        """
        MERGE (d:Document {fileName: $file_name})
        SET d.updatedAt = datetime()
        MERGE (c:Chunk {id: $chunk_id})
        SET c.text = $chunk_text,
            c.updatedAt = datetime()
        MERGE (c)-[:PART_OF]->(d)
        WITH c
        UNWIND $nodes AS row
        MERGE (e:__Entity__ {id: row.node_id})
        SET e.entityType = row.node_type,
            e.description = row.description,
            e.updatedAt = datetime()
        MERGE (c)-[:HAS_ENTITY]->(e)
        """,
        file_name=file_name,
        chunk_id=chunk_id,
        chunk_text=chunk_text,
        nodes=[node.__dict__ for node in nodes],
    )


def write_relationships(
    tx: Transaction,
    relationships: list[ExtractedRelationship],
) -> None:
    """按白名单关系类型写入实体关系。"""
    for relation_type in ALLOWED_RELATION_TYPES:
        rows = [
            relationship.__dict__
            for relationship in relationships
            if relationship.relation_type == relation_type
        ]
        if not rows:
            continue
        tx.run(
            f"""
            UNWIND $rows AS row
            MATCH (source:__Entity__ {{id: row.source_id}})
            MATCH (target:__Entity__ {{id: row.target_id}})
            MERGE (source)-[rel:{relation_type}]->(target)
            SET rel.description = row.description,
                rel.updatedAt = datetime()
            """,
            rows=rows,
        )


def main() -> None:
    """用模拟 GraphDocument 结果演示写库流程。"""
    chunk_text = "知识图谱构建器 uses LangChain and stores extracted entities in Neo4j."
    nodes = [
        ExtractedNode("知识图谱构建器", "Project", "课程中的示例项目"),
        ExtractedNode("LangChain", "Library", "用于 LLM 应用编排"),
        ExtractedNode("Neo4j", "Database", "图数据库"),
    ]
    relationships = [
        ExtractedRelationship("知识图谱构建器", "USES", "LangChain"),
        ExtractedRelationship("知识图谱构建器", "STORES_IN", "Neo4j"),
    ]

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            session.execute_write(create_constraints)
            session.execute_write(
                write_chunk_and_nodes,
                "lesson06-demo.md",
                "lesson06-c1",
                chunk_text,
                nodes,
            )
            session.execute_write(write_relationships, relationships)
            print("已写入 lesson06-demo.md 的抽取图谱")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
