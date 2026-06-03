# 15 拓展：企业级知识图谱工程阻碍与成熟方案

## 引言

企业级知识图谱最难的地方不在“能不能抽出节点和边”，而在“能不能长期维护一个可信、可更新、可查询、成本可控的图谱”。这一课专门讨论真实阻碍点，以及外部成熟产品通常怎么处理。

## 阻碍一：增量更新

文档、数据库和业务事件每天都在变化。如果每次都全量重建图谱，成本很高，旧答案也可能和新数据冲突。

成熟做法：

- 使用稳定主键和 upsert。
- 保存 `updatedAt`、版本号和来源哈希。
- 只重算受影响的 chunk、实体、关系和社区摘要。
- 对时间敏感事实建立 temporal edges，例如 `validFrom`、`validTo`。

本项目体现：chunk 用内容 SHA1 做 id，`Document` 记录 `processed_chunk` 和 `retry_condition`，可以从上次位置继续。

## 阻碍二：删除与级联影响

删除一个文档不只是删一行数据。它可能影响 chunk、实体、关系、社区、索引、问答来源。

成熟做法：

- 区分“删除来源文档”和“删除实体事实”。
- 删除前检查实体是否被其他文档引用。
- 删除后清理孤立节点和无引用社区。
- 保留审计日志，避免误删不可恢复。

本项目体现：`delete_file_from_graph` 支持删除 Document/Chunk，并可选择删除不再被其他文档引用的实体。

## 阻碍三：Schema 漂移

LLM 可能抽出 `Company`、`Organization`、`Org`、`Business`。如果不治理，图谱很快变成“同义词垃圾场”。

成熟做法：

- Schema-first 抽取。
- allowed nodes / allowed relationships。
- 定期 schema consolidation。
- 人工审批新增类型。
- 用本体或 SHACL/约束做质量检查。

本项目体现：`allowedNodes`、`allowedRelationship`、`graph_schema_consolidation`。

## 阻碍四：环与路径爆炸

用户提到“结构不能成环”。严格说，知识图谱不是不能成环，很多真实关系天然成环。例如 A 投资 B，B 合作 C，C 又收购 A。但工程上需要避免**无意义环**和**遍历爆炸**。

成熟做法：

- 给关系分类型，限制哪些关系可参与推理。
- 查询时限制 hop 数，例如 1..3 跳。
- 避免在 RAG 中无差别展开所有路径。
- 对高连接节点做降权，例如“美国”“公司”“产品”这类超级节点。
- 对层级关系保持 DAG 约束，例如组织层级、目录树、社区父子层级。

## 阻碍五：构建成本

LLM 抽取每个 chunk 都要花 token。大规模文档会让成本、延迟和失败率快速上升。

成熟做法：

- 先用规则或结构化字段确定 strong nodes。
- 只对高价值 chunk 做 LLM 抽取。
- 缓存抽取结果。
- 使用小模型/领域模型处理简单抽取，大模型处理复杂关系。
- 批处理和异步任务队列。

本项目体现：分批处理 chunk、记录 token usage、支持多模型 provider。

## 阻碍六：检索策略选择

不是所有问题都适合 GraphRAG。简单问题用向量检索更快；结构化计数用 Cypher 更准；全局总结需要社区摘要。

成熟做法：

- 建立 query router。
- 同时支持 vector、fulltext、graph expansion、entity vector、community/global search、Text2Cypher。
- 记录每种模式的准确率、延迟和成本。

本项目体现：`vector`、`fulltext`、`graph_vector`、`graph_vector_fulltext`、`entity_vector`、`global_vector`、`graph` 多种 chat mode。

## 阻碍七：权限与治理

企业图谱可能连接客户、合同、财务、人事数据。GraphRAG 一旦跨越权限边界，就会把敏感上下文交给 LLM。

成熟做法：

- 保留数据源权限。
- 查询前做访问控制过滤。
- 对不同用户生成不同可见子图。
- 对 LLM 上下文做脱敏。
- 记录查询审计。

Stardog、Neo4j Virtual Graph 等虚拟图方案的价值之一，就是让数据留在原系统，尽量继承原有治理控制。

## 企业级产品与方案对照

| 产品/方案 | 主要特点 | 适合解决的问题 |
|---|---|---|
| Neo4j | 属性图、Cypher、GDS、GraphRAG Python、可视化生态 | 工程图谱、路径查询、GraphRAG、图算法 |
| Amazon Neptune + Bedrock | 托管图数据库/图分析，与 Bedrock Knowledge Bases 结合 | 云上 RAG、托管运维、AWS 生态集成 |
| Stardog | 企业知识图谱、虚拟图、语义层、推理和治理 | 多源数据统一、零拷贝语义层、Agent 上下文 |
| Ontotext GraphDB | RDF/SPARQL、语义搜索、企业知识图谱治理 | 标准语义网、本体、语义数据管理 |
| TigerGraph | 大规模并行图数据库、GraphRAG/混合搜索方向 | 大图分析、高吞吐图查询、企业 AI 图基础设施 |

## 企业级验收清单

上线前至少检查：

| 维度 | 检查项 |
|---|---|
| 数据权限 | chunk、document、entity 是否带权限字段；检索前是否过滤无权限来源 |
| 审计日志 | 谁触发了抽取、删除、合并、社区重算；是否能追踪 |
| 删除恢复 | 是否支持软删除、误删回滚、共享实体保护 |
| Schema 变更 | 新增 label/relationship 是否审批；旧关系如何迁移 |
| 评估集 | 是否有实体、关系、问答、引用来源的人工标注样本 |
| 服务指标 | 平均延迟、失败率、token 成本、索引刷新时间是否有阈值 |
| 重试策略 | LLM 超时、数据库死锁、任务取消后是否能从断点恢复 |
| 监控指标 | 重复实体率、孤立节点率、schema drift、无来源答案率是否可见 |

## 源码导读

建议阅读：

- `backend/src/main.py`：状态机、分批处理、token usage、失败续跑。
- `backend/src/graphDB_dataAccess.py`：删除、死锁重试、去重、孤立节点、索引重建。
- `backend/src/post_processing.py`：schema consolidation 和索引治理。
- `backend/src/communities.py`：社区检测、社区摘要、社区索引。
- `backend/src/QA_integration.py`：多检索模式、问题改写、上下文拼装。

阅读问题：

- 如果一个文档更新了，哪些节点和索引必须重新计算？
- 如果误合并了两个实体，系统如何回滚？
- 如果用户没有某个文档权限，GraphRAG 如何避免把该文档 chunk 放进上下文？

## 小结

企业级知识图谱不是“把 Neo4j 跑起来”就完成了。真正的挑战是增量、删除、schema、成本、检索、权限、评估和治理。成熟方案通常不是单点工具，而是一套图数据库、语义层、索引、任务系统、评估系统和权限系统的组合。
