# 08 图数据库与查询语言：知识图谱增删改查

## 引言

MySQL 的 CRUD 多数围绕表和行。知识图谱的 CRUD 更复杂，因为一次修改可能影响节点、关系、路径、索引、社区、溯源和问答结果。

## Neo4j 属性图

Neo4j 用节点、关系和属性表达数据：

```cypher
(:Document {fileName: "paper.pdf"})
(:Chunk {id: "sha1", text: "..."})
(:Chunk)-[:HAS_ENTITY]->(:Company {id: "Neo4j"})
```

节点可以有多个 label，关系有方向和类型，节点与关系都可以有属性。

## 常用 CRUD

**创建或更新**通常用 `MERGE`，因为图谱构建任务经常重试，幂等性很重要。

```cypher
MERGE (d:Document {fileName: $fileName})
SET d.status = "Processing", d.updatedAt = datetime()
```

**查询**常用模式匹配：

```cypher
MATCH (d:Document)<-[:PART_OF]-(c:Chunk)-[:HAS_ENTITY]->(e)
WHERE d.fileName = $fileName
RETURN c.position, e.id
```

**删除**要谨慎。删除节点前必须处理关系，常用 `DETACH DELETE`。但如果实体被多个文档共享，不能随便删。

## 为什么比 MySQL 复杂

图谱删除一个文档时，至少要问：

- 删除 `Document` 后，相关 `Chunk` 要不要删？
- `Chunk` 指向的实体是否还被其他文档引用？
- 社区节点是否变成无引用？
- 向量索引、全文索引、计数统计是否需要更新？
- GraphRAG 返回的来源是否还有效？

本项目 `delete_file_from_graph` 就分成“只删文档与 chunk”和“同时删不再被其他文档引用的实体”两种策略，并额外清理无引用社区。

## 索引与约束

知识图谱系统至少需要：

- 实体 id 索引或唯一约束。
- Chunk embedding vector index。
- Entity embedding vector index。
- Chunk text fulltext index。
- Community summary fulltext/vector index。

索引不是性能细节，而是检索模式能否成立的前提。

## 小结

Cypher 的语法不难，难的是图谱操作的副作用。企业知识图谱必须把增删改查和溯源、共享实体、索引、社区、问答结果一起设计。

## 源码导读

建议阅读本项目这些位置：

- `backend/src/graphDB_dataAccess.py`：看 `create_source_node`、`delete_file_from_graph`、`drop_create_vector_index`，理解真实项目如何创建、删除、重建索引。
- `backend/src/shared/constants.py`：阅读图可视化和删除相关查询，观察复杂查询如何组织。
- `backend/score.py`：查看 `/delete_document_and_entities`、`/graph_query`、`/drop_create_vector_index` 如何把 API 映射到图谱操作。

阅读问题：

- 删除一个文档时，哪些实体不能删？
- 为什么向量索引维度和 embedding 模型必须一致？
- 为什么批量写入更适合用 `UNWIND`？
