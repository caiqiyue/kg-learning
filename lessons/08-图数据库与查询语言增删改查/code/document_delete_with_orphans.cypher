// 删除文档并清理孤立实体示例。
// 场景：删除一个来源文档时，不能误删仍被其他文档引用的共享实体。
// 参数示例：
// :param fileName => "demo.pdf";

// 1. 先预览要删除的文档、chunk 和候选实体。
//    这一步只 RETURN，不删除，适合在 Neo4j Browser 中人工确认。
MATCH (d:Document {fileName: $fileName})<-[:PART_OF]-(c:Chunk)
OPTIONAL MATCH (c)-[:HAS_ENTITY]->(e:__Entity__)
RETURN d.fileName AS document,
       count(DISTINCT c) AS chunkCount,
       collect(DISTINCT e.id)[0..20] AS candidateEntities;

// 2. 收集候选实体 id，再删除 Document 与 Chunk。
//    注意：不能先删 chunk，否则后面就不知道哪些实体需要检查。
MATCH (d:Document {fileName: $fileName})
OPTIONAL MATCH (d)<-[:PART_OF]-(c:Chunk)
OPTIONAL MATCH (c)-[:HAS_ENTITY]->(e:__Entity__)
WITH d, collect(DISTINCT c) AS chunks, collect(DISTINCT e.id) AS candidateEntityIds
FOREACH (chunk IN chunks | DETACH DELETE chunk)
DETACH DELETE d
WITH candidateEntityIds

// 3. 只检查“本次删除文档曾经引用过”的实体。
//    如果实体仍被其他 chunk 引用，说明它是共享实体，必须保留。
// 注意：真实生产环境建议先 RETURN 给人工确认，再 DELETE。
UNWIND candidateEntityIds AS entityId
MATCH (e:__Entity__)
WHERE e.id = entityId
  AND NOT EXISTS {
  MATCH (:Chunk)-[:HAS_ENTITY]->(e)
}
  AND NOT EXISTS {
  MATCH (e)-[r]-(:__Entity__)
  WHERE type(r) <> "HAS_ENTITY"
}
DETACH DELETE e;

// 4. 清理没有成员的社区节点。
//    这一步依然只删除无成员社区，不影响仍有关联实体的社区。
MATCH (community:__Community__)
WHERE NOT EXISTS {
  MATCH (:__Entity__)-[:IN_COMMUNITY]->(community)
}
DETACH DELETE community;
