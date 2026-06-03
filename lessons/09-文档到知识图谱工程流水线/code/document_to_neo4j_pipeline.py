"""最小可运行的文档到 Neo4j 知识图谱流水线。

运行前需要安装:
    pip install neo4j

这个例子不调用 LLM，而是用规则模拟抽取，重点学习工程流水线。
"""

import hashlib
import os
from neo4j import GraphDatabase


NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")


def sha1_text(text: str) -> str:
    """用文本内容生成稳定 id，保证重试时不会重复创建 chunk。"""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def split_text(text: str, size: int = 80) -> list[str]:
    """真实项目按 token 切分；这里按字符切分，方便本地理解。"""
    return [text[index:index + size] for index in range(0, len(text), size)]


def mock_extract_entities(text: str) -> list[dict]:
    """模拟实体抽取结果；真实项目会调用 LLMGraphTransformer。"""
    entities = []
    if "Neo4j" in text:
        entities.append({"id": "Neo4j", "label": "Database"})
    if "LangChain" in text:
        entities.append({"id": "LangChain", "label": "Library"})
    if "GraphRAG" in text:
        entities.append({"id": "GraphRAG", "label": "Method"})
    return entities


def write_document(tx, file_name: str) -> None:
    """写入 Document，并把状态设置为 Processing。"""
    tx.run(
        """
        MERGE (d:Document {fileName: $file_name})
        SET d.status = 'Processing',
            d.updatedAt = datetime()
        """,
        file_name=file_name,
    )


def write_chunk_and_entities(tx, file_name: str, chunk_text: str, position: int) -> None:
    """写入 chunk、实体和 HAS_ENTITY 溯源关系。"""
    chunk_id = sha1_text(chunk_text)
    entities = mock_extract_entities(chunk_text)
    tx.run(
        """
        MATCH (d:Document {fileName: $file_name})
        MERGE (c:Chunk {id: $chunk_id})
        SET c.text = $chunk_text,
            c.position = $position,
            c.updatedAt = datetime()
        MERGE (c)-[:PART_OF]->(d)
        WITH c
        UNWIND $entities AS entity
        CALL apoc.merge.node(['__Entity__', entity.label], {id: entity.id}) YIELD node AS e
        MERGE (c)-[:HAS_ENTITY]->(e)
        """,
        file_name=file_name,
        chunk_id=chunk_id,
        chunk_text=chunk_text,
        position=position,
        entities=entities,
    )


def mark_completed(tx, file_name: str) -> None:
    """处理完成后更新 Document 状态。"""
    tx.run(
        """
        MATCH (d:Document {fileName: $file_name})
        SET d.status = 'Completed',
            d.updatedAt = datetime()
        """,
        file_name=file_name,
    )


def main() -> None:
    """执行一次端到端导入。"""
    # 这段文本模拟一个被上传的文档内容，真实系统会从 PDF/网页/视频字幕中读取。
    text = "Neo4j 和 LangChain 可以共同构建 GraphRAG。GraphRAG 通过实体关系帮助大模型获得更可靠的上下文。"
    # 创建数据库连接；真实项目建议在应用生命周期内复用 driver，而不是每次请求都新建。
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            # 第一步：创建 Document，并把状态置为 Processing，表示长任务开始。
            session.execute_write(write_document, "lesson-demo.txt")
            # 第二步：逐个 chunk 写入图数据库；每个 chunk 都会挂到 Document 上，保留来源。
            for position, chunk in enumerate(split_text(text), start=1):
                session.execute_write(write_chunk_and_entities, "lesson-demo.txt", chunk, position)
            # 第三步：全部 chunk 成功后再标记 Completed，避免半成品被误认为可用。
            session.execute_write(mark_completed, "lesson-demo.txt")
    finally:
        # 关闭连接，释放网络资源。
        driver.close()


if __name__ == "__main__":
    main()
