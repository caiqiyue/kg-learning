# 代码说明

把 `.cypher` 文件放到 Neo4j Browser 或 cypher-shell 中分段执行。

练习重点不是记语法，而是观察：

- 为什么 `MERGE` 适合图谱构建重试。
- 为什么删除文档时不一定删除实体。
- 为什么 `HAS_ENTITY` 是 GraphRAG 溯源的重要关系。

建议顺序：

1. `cypher_indexes_constraints.cypher`：先建约束和索引。
2. `cypher_crud_examples.cypher`：理解单条 CRUD。
3. `bulk_import_unwind.cypher`：理解批量导入。
4. `cypher_advanced_queries.cypher`：练习路径、邻域、聚合和分页。
5. `document_delete_with_orphans.cypher`：练习安全删除。
6. `neo4j_driver_crud.py` 与 `python_transaction_batch.py`：用 Python Driver 执行同类流程。
