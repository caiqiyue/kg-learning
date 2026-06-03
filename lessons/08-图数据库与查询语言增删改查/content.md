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

成熟系统通常会把删除分成“只删文档与 chunk”和“同时删不再被其他文档引用的实体”两种策略，并额外清理无引用社区。

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

## 工程阅读任务

阅读任何知识图谱系统的增删改查设计时，可以重点寻找这些模块：

- 数据写入模块：是否使用 `MERGE`、唯一约束和批量 `UNWIND` 保证幂等。
- 删除模块：是否区分来源删除、实体删除、共享实体保护和索引刷新。
- 查询模块：是否把业务 API 映射到稳定的 Cypher 查询模板。
- 索引模块：是否能重建向量索引、全文索引和实体唯一约束。

阅读问题：

- 删除一个文档时，哪些实体不能删？
- 为什么向量索引维度和 embedding 模型必须一致？
- 为什么批量写入更适合用 `UNWIND`？
