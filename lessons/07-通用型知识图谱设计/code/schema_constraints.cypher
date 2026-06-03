// 通用型知识图谱的基础约束和索引。
// 执行前提：Neo4j 5.x，且数据库用户有创建约束和索引的权限。

// Document 使用 fileName 作为主键，避免同一个文件被重复创建。
CREATE CONSTRAINT document_file_name IF NOT EXISTS
FOR (d:Document)
REQUIRE d.fileName IS UNIQUE;

// Chunk 使用内容 hash 或业务生成 id 作为主键，便于重试和增量更新。
CREATE CONSTRAINT chunk_id IF NOT EXISTS
FOR (c:Chunk)
REQUIRE c.id IS UNIQUE;

// __Entity__ 使用 id 作为主键，减少重复实体。
CREATE CONSTRAINT entity_id IF NOT EXISTS
FOR (e:__Entity__)
REQUIRE e.id IS UNIQUE;

// __Community__ 使用 id 作为主键，避免社区重复写入。
CREATE CONSTRAINT community_id IF NOT EXISTS
FOR (c:__Community__)
REQUIRE c.id IS UNIQUE;

// Chunk 文本全文索引用于关键词检索，例如文件编号、专有名词。
CREATE FULLTEXT INDEX chunk_text IF NOT EXISTS
FOR (c:Chunk)
ON EACH [c.text];

// 实体全文索引用于按实体名称或描述查找节点。
CREATE FULLTEXT INDEX entity_text IF NOT EXISTS
FOR (e:__Entity__)
ON EACH [e.id, e.description];

// Chunk 向量索引用于语义相似检索。
// dimensions 需要和 embedding 模型输出维度一致。
CREATE VECTOR INDEX chunk_vector IF NOT EXISTS
FOR (c:Chunk)
ON (c.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};
