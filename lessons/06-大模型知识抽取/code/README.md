# 代码说明

运行：

```bash
python llm_extraction_prompt.py
```

这个例子不调用真实模型，只展示 schema 约束如何进入提示词。真实系统可以把同类约束传给 `LLMGraphTransformer`、函数调用、Pydantic 输出或其他结构化抽取组件。

建议学习顺序：

1. `llm_extraction_prompt.py`：观察 schema、规则和输出格式如何写进提示词。
2. `validate_graph_output.py`：理解最小 schema 过滤。
3. `schema_driven_extraction_pipeline.py`：学习实体 id 规范化、关系签名校验、拒绝原因记录和 chunk 溯源。
4. `langchain_graph_transformer_demo.py`：调用 LangChain `LLMGraphTransformer` 生成 `GraphDocument`。
5. `write_graph_documents_to_neo4j.py`：把抽取结果写入 Neo4j，并保留 `Document`、`Chunk`、`HAS_ENTITY` 来源。
