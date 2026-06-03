// KNN: 为每个 Chunk 找相似 Chunk，写 SIMILAR 关系。
MATCH (c:Chunk)
WHERE c.embedding IS NOT NULL AND count { (c)-[:SIMILAR]-() } < 5
CALL db.index.vector.queryNodes('vector', 6, c.embedding)
YIELD node, score
WHERE node <> c AND score >= 0.8
MERGE (c)-[rel:SIMILAR]-(node)
SET rel.score = score;

// 查找孤立实体：没有连接到其他实体。
MATCH (e:!Chunk&!Document&!`__Community__`)
WHERE NOT exists { (e)--(:!Chunk&!Document&!`__Community__`) }
RETURN e.id AS id, labels(e) AS labels
ORDER BY id
LIMIT 100;

// 删除用户确认后的孤立节点。
MATCH (e)
WHERE elementId(e) IN $elementIds
DETACH DELETE e;

// 创建 Community 唯一约束。
CREATE CONSTRAINT IF NOT EXISTS
FOR (c:__Community__)
REQUIRE c.id IS UNIQUE;

// 查看社区摘要。
MATCH (c:__Community__)
WHERE c.summary IS NOT NULL
RETURN c.id, c.title, c.summary
ORDER BY c.community_rank DESC
LIMIT 20;
