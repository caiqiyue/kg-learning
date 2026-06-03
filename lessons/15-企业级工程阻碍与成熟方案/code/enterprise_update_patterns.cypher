// 这个文件展示企业级知识图谱常见的增量更新和删除模式。
// 每段都应该先在测试库执行，确认不会误删生产数据。

// 1. 使用稳定主键做文档 upsert。
// MERGE 可以保证同一个 sourceId 多次处理时不会重复创建 Document。
MERGE (d:Document {sourceId: $sourceId})
SET d.fileName = $fileName,
    d.sourceHash = $sourceHash,
    d.updatedAt = datetime(),
    d.status = "Processing";

// 2. 只处理内容 hash 变化的 chunk。
// 如果 chunkHash 没变，就不需要重复抽取实体，能显著降低 LLM 成本。
MATCH (d:Document {sourceId: $sourceId})
MERGE (c:Chunk {id: $chunkId})
ON CREATE SET c.text = $text,
              c.chunkHash = $chunkHash,
              c.position = $position,
              c.createdAt = datetime()
ON MATCH SET c.position = $position,
             c.updatedAt = datetime()
MERGE (c)-[:PART_OF]->(d);

// 3. 标记旧关系失效，而不是立刻物理删除。
// 这样可以保留审计历史，并支持时间范围查询。
MATCH (s:__Entity__ {id: $sourceEntity})-[r]->(t:__Entity__ {id: $targetEntity})
WHERE type(r) = $relationshipType AND r.validTo IS NULL
SET r.validTo = datetime(),
    r.status = "Expired";

// 4. 删除某个文档时，只删除不再被其他文档引用的实体。
// 这避免把共享实体一起误删。
MATCH (d:Document {sourceId: $sourceId})
OPTIONAL MATCH (d)<-[:PART_OF]-(c:Chunk)
OPTIONAL MATCH (c)-[:HAS_ENTITY]->(e)
WITH d, collect(DISTINCT c) AS chunks, collect(DISTINCT e) AS entities
FOREACH (chunk IN chunks | DETACH DELETE chunk)
WITH d, entities
UNWIND entities AS entity
WITH d, entity
WHERE entity IS NOT NULL
  AND NOT EXISTS {
    MATCH (entity)<-[:HAS_ENTITY]-(:Chunk)-[:PART_OF]->(:Document)
  }
DETACH DELETE entity
DETACH DELETE d;

// 5. 遍历时限制 hop，避免路径爆炸。
// 企业问答中通常先从 1 到 3 跳开始，不建议默认无限展开。
MATCH path = (:__Entity__ {id: $entityId})-[*1..3]-(:__Entity__)
RETURN path
LIMIT 50;
