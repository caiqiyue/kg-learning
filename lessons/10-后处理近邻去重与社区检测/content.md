# 10 后处理：近邻、去重、孤立节点与社区检测

## 引言

知识图谱建立后，真正的工程工作才刚开始。LLM 抽取出的图通常会有重复实体、孤立节点、关系命名漂移、schema 不一致和检索索引缺失。

## KNN 与 SIMILAR

本项目会查询 Neo4j vector index，把 embedding 相近的 chunk 用 `SIMILAR` 关系连接起来。这样检索到一个 chunk 后，可以扩展到语义相近的其他 chunk。

通俗地说，KNN 就像“帮一篇文章找最像它的几篇文章”。它不是说两篇文章有事实关系，而是说它们语义上接近。知识图谱里要把这种相似边和事实边分开。

KNN 关系不是原文事实，而是后处理生成的相似性边。课程里要明确区分：

- 知识关系：`Company ACQUIRED Company`
- 溯源关系：`Chunk HAS_ENTITY Entity`
- 结构关系：`Chunk NEXT_CHUNK Chunk`
- 相似关系：`Chunk SIMILAR Chunk`

## 去重

LLM 可能抽出 `OpenAI`、`Open AI`、`OpenAI Inc.`。本项目使用字符串包含、APOC 编辑距离、embedding cosine 和 label 一致性找重复，再用 `apoc.refactor.mergeNodes` 合并。

实体去重必须谨慎。相似不等于相同，尤其在人名、缩写、产品版本里。

## 孤立节点

孤立节点是没有领域关系的实体。它可能是噪声，也可能是重要但暂时没连上的实体。工程上一般先列出给用户确认，再删除。

## 社区检测

项目使用 GDS Leiden 做社区检测，把实体划分到 `__Community__`，再生成 `IN_COMMUNITY` 和 `PARENT_COMMUNITY`。随后用 LLM 给社区生成摘要，并为社区摘要建立向量和全文索引。

社区可以理解成朋友圈或部门小团体：有些实体彼此联系特别密集，就很可能围绕同一个主题。比如“GraphRAG、Chunk、Entity、Community、Neo4jVector”经常连在一起，它们可能组成“图谱增强检索”社区。

这一步直接服务 GraphRAG 的全局搜索：用户问“这批文档整体讲了哪些主题”时，社区摘要比单个 chunk 更合适。

## 小结

后处理决定知识图谱能否从 demo 走向生产。一个好图谱不是抽取得到的，而是抽取、清洗、合并、索引、评估和治理共同得到的。

## 源码导读

建议阅读：

- `backend/src/graphDB_dataAccess.py`：`update_KNN_graph`、`get_duplicate_nodes_list`、`merge_duplicate_nodes`、`list_unconnected_nodes`。
- `backend/src/post_processing.py`：`create_vector_fulltext_indexes`、`create_entity_embedding`、`graph_schema_consolidation`。
- `backend/src/communities.py`：`create_community_graph_projection`、`write_communities`、`create_community_summaries`。

阅读问题：

- 哪些后处理可以自动执行，哪些应该先让人确认？
- 近邻关系 `SIMILAR` 是事实关系吗？
- 社区摘要过期后，应该全量重算还是局部重算？
