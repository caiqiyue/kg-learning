# llm-graph-builder 项目阅读笔记

## 项目定位

`llm-graph-builder` 是一个把 PDF、网页、YouTube、Wikipedia、S3/GCS 等数据源转换为 Neo4j 知识图谱的应用。后端使用 FastAPI、LangChain、Neo4j Python Driver、LangChain Neo4j、Graph Data Science；前端使用 React 和 Neo4j NVL 做图谱预览。

## 核心流水线

1. `backend/score.py` 暴露 API，例如 `/extract`、`/url/scan`、`/post_processing`、`/chat_bot`、`/graph_query`、`/delete_document_and_entities`。
2. `backend/src/main.py` 创建数据源节点，并在 `processing_source` 中组织主处理流程。
3. `backend/src/create_chunks.py` 用 `TokenTextSplitter` 把文档切成 chunk。
4. `backend/src/make_relationships.py` 为 chunk 创建 `PART_OF`、`FIRST_CHUNK`、`NEXT_CHUNK`，并写入 embedding 和 vector index。
5. `backend/src/llm.py` 使用 `LLMGraphTransformer` 或 Diffbot 从 chunk 抽取节点、关系和描述。
6. `backend/src/shared/common_fn.py` 的保存逻辑把 `GraphDocument` 写入 Neo4j。
7. `backend/src/make_relationships.py` 再建立 `(:Chunk)-[:HAS_ENTITY]->(:Entity)`。
8. `backend/src/graphDB_dataAccess.py` 负责 Document 状态、删除、KNN、孤立节点、重复节点合并、向量索引重建。
9. `backend/src/communities.py` 使用 GDS Leiden 写 community，生成 `__Community__` 节点、父子社区、摘要、embedding 和索引。
10. `backend/src/QA_integration.py` 支持 vector、fulltext、entity_vector、graph_vector、graph_vector_fulltext、global_vector 等问答模式。

## 课程借鉴点

- 知识图谱不是一次性抽取结果，而是一条可恢复、可重试、可删除、可后处理的工程流水线。
- 通用型 KG 需要 `Document/Chunk/Entity/Community` 分层，否则很难同时支持溯源、检索、问答和图算法。
- LLM 抽取需要 schema 约束、追加指令、结构化输出、后处理和人工可视化检查。
- GraphRAG 不只是“多加一个图数据库”，而是 chunk 向量检索、实体邻域扩展、全文检索、社区摘要和 Cypher 查询的组合策略。

## 子智能体项目阅读摘要

子智能体补充确认了以下课程重点：

- 前端通过 Axios 将 Neo4j 凭证随请求传给后端，而不是直接连接 Neo4j；这适合讲企业应用中的连接上下文与权限边界。
- `backend/score.py` 的 API surface 可以映射为课程工程流：`/extract`、`/post_processing`、`/chat_bot`、`/graph_query`、`/delete_document_and_entities`。
- `backend/src/main.py` 是端到端抽取流水线案例，包含状态机、分批处理、取消、重试、token usage 和延迟指标。
- `backend/src/graphDB_dataAccess.py` 是图谱 CRUD 与治理案例，包含文档删除、共享实体保留、KNN、孤立节点、重复节点合并和索引重建。
- `backend/src/communities.py` 是 GraphRAG 全局检索案例，使用 GDS Leiden 生成社区、父社区、社区摘要和社区向量索引。
- `backend/src/QA_integration.py` 是多模式 GraphRAG 案例，适合比较 vector、fulltext、graph_vector、graph_vector_fulltext、entity_vector、global_vector 和 GraphCypherQA。
- 前端图谱可视化、Graph Enhancement Dialog 和 ChatBot 多模式对比，可以作为课程演示材料。

这些点已经体现在第 07-12 课的工程章节中。
