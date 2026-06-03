// UNWIND 批量导入示例。
// 输入参数 $rows 是一个列表，每一项包含 chunkId、text、position、fileName。
// 适用场景：一次写入多个 chunk，比循环发送多条 Cypher 更高效。

UNWIND $rows AS row
MATCH (d:Document {fileName: row.fileName})
MERGE (c:Chunk {id: row.chunkId})
SET c.text = row.text,
    c.position = row.position,
    c.updatedAt = datetime()
MERGE (c)-[:PART_OF]->(d);

// 如果需要连接连续 chunk，可以另外传入 $links。
// $links 的每一项包含 previousId 和 currentId。

UNWIND $links AS link
MATCH (previous:Chunk {id: link.previousId})
MATCH (current:Chunk {id: link.currentId})
MERGE (previous)-[:NEXT_CHUNK]->(current);
