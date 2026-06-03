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

// 如果需要同时写入实体，可以传入 $entities。
// $entities 的每一项包含 chunkId、entityId、entityType。
// 注意：Cypher 不能直接把 label 参数化。教学示例统一写入 __Entity__，
// 具体类型放到 entityType 属性；生产系统也可以使用白名单 + APOC 写动态 label。

UNWIND $entities AS entity
MATCH (c:Chunk {id: entity.chunkId})
MERGE (e:__Entity__ {id: entity.entityId})
SET e.entityType = entity.entityType,
    e.updatedAt = datetime()
MERGE (c)-[:HAS_ENTITY]->(e);

// 如果需要写入实体之间的关系，可以传入 $relationships。
// 这里用 CASE 限制关系类型，避免把任意模型输出直接变成数据库关系。

UNWIND $relationships AS row
MATCH (source:__Entity__ {id: row.sourceId})
MATCH (target:__Entity__ {id: row.targetId})
FOREACH (_ IN CASE WHEN row.type = 'USES' THEN [1] ELSE [] END |
  MERGE (source)-[:USES]->(target)
)
FOREACH (_ IN CASE WHEN row.type = 'SUPPORTS' THEN [1] ELSE [] END |
  MERGE (source)-[:SUPPORTS]->(target)
)
FOREACH (_ IN CASE WHEN row.type = 'MENTIONS' THEN [1] ELSE [] END |
  MERGE (source)-[:MENTIONS]->(target)
);
