// Chunk 和 Entity 向量索引示例。
// dimensions 必须与 embedding 模型一致；如果模型改变，需要重建索引。

CREATE VECTOR INDEX chunk_vector IF NOT EXISTS
FOR (c:Chunk)
ON (c.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

CREATE VECTOR INDEX entity_vector IF NOT EXISTS
FOR (e:__Entity__)
ON (e.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// 使用向量索引查找和某个 chunk 最相似的其他 chunk。
MATCH (c:Chunk {id: $chunkId})
CALL db.index.vector.queryNodes('chunk_vector', 5, c.embedding)
YIELD node, score
WHERE node <> c
RETURN node.id AS similarChunkId,
       score
ORDER BY score DESC;
