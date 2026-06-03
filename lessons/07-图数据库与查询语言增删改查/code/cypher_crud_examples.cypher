// 创建文档节点：MERGE 让重复上传或重试更安全。
MERGE (d:Document {fileName: "demo.pdf"})
SET d.status = "New",
    d.createdAt = datetime(),
    d.nodeCount = 0,
    d.relationshipCount = 0;

// 创建 chunk，并把它挂到文档上。
MERGE (c:Chunk {id: "chunk-001"})
SET c.text = "Neo4j supports graph queries with Cypher.",
    c.position = 1
WITH c
MATCH (d:Document {fileName: "demo.pdf"})
MERGE (c)-[:PART_OF]->(d)
MERGE (d)-[:FIRST_CHUNK]->(c);

// 创建实体与关系。
MERGE (neo4j:Database:__Entity__ {id: "Neo4j"})
MERGE (cypher:QueryLanguage:__Entity__ {id: "Cypher"})
MERGE (neo4j)-[:SUPPORTS]->(cypher);

// 建立 chunk 到实体的溯源关系。
MATCH (c:Chunk {id: "chunk-001"})
MATCH (e:__Entity__ {id: "Neo4j"})
MERGE (c)-[:HAS_ENTITY]->(e);

// 查询一个文档抽取出的实体。
MATCH (d:Document {fileName: "demo.pdf"})<-[:PART_OF]-(c:Chunk)-[:HAS_ENTITY]->(e)
RETURN d.fileName AS file, c.position AS position, e.id AS entity;

// 更新文档状态和统计。
MATCH (d:Document {fileName: "demo.pdf"})
SET d.status = "Completed",
    d.updatedAt = datetime();

// 删除文档和 chunk，但保留可能被其他文档共享的实体。
MATCH (d:Document {fileName: "demo.pdf"})
OPTIONAL MATCH (d)<-[:PART_OF]-(c:Chunk)
DETACH DELETE c, d;
