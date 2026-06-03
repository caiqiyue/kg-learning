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

// 3. 查看根据 fileName 查询时是否使用索引。
EXPLAIN
MATCH (d:Document {fileName: $fileName})
RETURN d;

// 4. 查看真实执行代价。
PROFILE
MATCH (d:Document {fileName: $fileName})<-[:PART_OF]-(c:Chunk)
RETURN count(c) AS chunkCount;
