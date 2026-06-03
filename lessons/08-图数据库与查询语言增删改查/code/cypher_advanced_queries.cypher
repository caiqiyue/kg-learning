// Neo4j/Cypher 进阶查询示例：路径、多跳、聚合、分页。
// 这些查询适合在 Neo4j Browser 或 cypher-shell 中分段执行。

// 1. 查询某个文档中的实体及其 1 跳邻居。
// 用途：GraphRAG 命中 chunk 后，扩展实体邻域作为上下文。
MATCH (d:Document {fileName: $fileName})<-[:PART_OF]-(c:Chunk)-[:HAS_ENTITY]->(e)
OPTIONAL MATCH (e)-[r]-(neighbor)
WHERE neighbor:__Entity__
RETURN c.id AS chunkId,
       e.id AS entityId,
       type(r) AS relationType,
       neighbor.id AS neighborId
ORDER BY chunkId, entityId
LIMIT 100;

// 2. 查询两个实体之间 1 到 3 跳路径。
// 注意：生产查询必须限制最大跳数，否则容易发生路径爆炸。
MATCH path = (a:__Entity__ {id: $sourceId})-[*1..3]-(b:__Entity__ {id: $targetId})
RETURN path
LIMIT 20;

// 3. 统计每个实体被多少 chunk 提到。
// 用途：判断实体是否重要，也能发现“超级节点”。
MATCH (c:Chunk)-[:HAS_ENTITY]->(e:__Entity__)
RETURN e.id AS entityId,
       labels(e) AS labels,
       count(DISTINCT c) AS mentionCount
ORDER BY mentionCount DESC
LIMIT 50;

// 4. 查询孤立实体：没有任何领域关系，只被 chunk 提到。
// 用途：找噪声实体或需要补边的实体。
MATCH (e:__Entity__)
WHERE NOT EXISTS {
  MATCH (e)-[r]-(:__Entity__)
  WHERE type(r) <> "HAS_ENTITY"
}
RETURN e.id AS isolatedEntityId, labels(e) AS labels
LIMIT 100;

// 5. 分页查看实体，避免一次返回过多结果。
// 参数：$skip 表示跳过多少行，$limit 表示返回多少行。
MATCH (e:__Entity__)
RETURN e.id AS entityId, labels(e) AS labels
ORDER BY entityId
SKIP $skip
LIMIT $limit;
