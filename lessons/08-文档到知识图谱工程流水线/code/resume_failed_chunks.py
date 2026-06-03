"""失败续跑示例：只处理还没有 HAS_ENTITY 的 chunk。"""

import os
from neo4j import GraphDatabase


NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")


def find_unprocessed_chunks(tx, file_name: str) -> list[dict]:
    """找出已经切分但还没有实体关系的 chunk。"""
    result = tx.run(
        """
        MATCH (d:Document {fileName: $file_name})<-[:PART_OF]-(c:Chunk)
        WHERE NOT EXISTS { (c)-[:HAS_ENTITY]->(:__Entity__) }
        RETURN c.id AS chunk_id,
               c.text AS text,
               c.position AS position
        ORDER BY c.position
        """,
        file_name=file_name,
    )
    return [record.data() for record in result]


def mark_retry_status(tx, file_name: str, processed_position: int) -> None:
    """记录续跑进度，避免任务再次失败后从头开始。"""
    tx.run(
        """
        MATCH (d:Document {fileName: $file_name})
        SET d.status = 'Processing',
            d.processed_chunk = $processed_position,
            d.retry_condition = 'start_from_last_processed_position',
            d.updatedAt = datetime()
        """,
        file_name=file_name,
        processed_position=processed_position,
    )


def main() -> None:
    """演示如何读取待续跑 chunk。"""
    # 连接 Neo4j；这里只演示续跑查询，不实际重新调用 LLM。
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            # 找出没有 HAS_ENTITY 的 chunk，通常表示抽取阶段失败或被中断。
            chunks = session.execute_read(find_unprocessed_chunks, "lesson-demo.txt")
            print("待续跑 chunk:", chunks)
            if chunks:
                # 把续跑起点写回 Document，下一次任务可以从这个位置继续。
                session.execute_write(mark_retry_status, "lesson-demo.txt", chunks[0]["position"])
    finally:
        # 无论成功或失败，都关闭 driver。
        driver.close()


if __name__ == "__main__":
    main()
