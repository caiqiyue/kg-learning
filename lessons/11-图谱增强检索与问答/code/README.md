# 代码说明

运行：

```bash
python retrieval_modes.py
```

真实系统不会只靠规则，但这个例子能帮助理解：GraphRAG 应该根据问题类型选择不同检索入口，而不是所有问题都走同一条链。

建议学习顺序：

1. `retrieval_modes.py`：先理解问题路由。
2. `local_graphrag_retriever.py`：看局部 GraphRAG 如何拼接 chunk、实体和邻域事实。
3. `neo4j_local_retriever.py`：用 Neo4j Driver 查询向量索引并扩展实体邻域。
4. `global_community_retriever.py`：看全局社区摘要如何进入上下文。
5. `hybrid_graphrag_pipeline.py`：把多路证据合并、去重、排序并拼成可引用上下文。
6. `graph_cypher_qa_demo.py`：学习白名单 Cypher 模板。
7. `cypher_qa_chain_langchain.py`：了解 LangChain GraphCypherQAChain 的基本用法和风险边界。
