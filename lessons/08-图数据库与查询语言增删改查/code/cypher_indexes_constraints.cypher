// 查询计划与索引示例。
// EXPLAIN 只看计划，不真正执行；PROFILE 会执行并显示实际代价。

// 1. 为 Document.fileName 创建唯一约束。
CREATE CONSTRAINT document_file_name_unique IF NOT EXISTS
FOR (d:Document)
REQUIRE d.fileName IS UNIQUE;

// 2. 为 Chunk.id 创建唯一约束。
CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS
FOR (c:Chunk)
REQUIRE c.id IS UNIQUE;

// 3. 为实体 id 创建唯一约束。
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (e:__Entity__)
REQUIRE e.id IS UNIQUE;

// 4. 为 Chunk.text 创建全文索引。
//    关键词精确检索和混合检索都会用到全文索引。
CREATE FULLTEXT INDEX chunk_text_fulltext IF NOT EXISTS
FOR (c:Chunk)
ON EACH [c.text];

// 5. 为 Chunk.embedding 创建向量索引。
//    vector.dimensions 必须和 embedding 模型输出维度一致。
CREATE VECTOR INDEX chunk_embedding_vector IF NOT EXISTS
FOR (c:Chunk)
ON (c.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// 6. 查看根据 fileName 查询时是否使用索引。
EXPLAIN
MATCH (d:Document {fileName: $fileName})
RETURN d;

// 7. 查看真实执行代价。
PROFILE
MATCH (d:Document {fileName: $fileName})<-[:PART_OF]-(c:Chunk)
RETURN count(c) AS chunkCount;
