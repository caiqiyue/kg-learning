# 代码说明

运行：

```bash
python llm_extraction_prompt.py
```

这个例子不调用真实模型，只展示 schema 约束如何进入提示词。真实系统可以把同类约束传给 `LLMGraphTransformer`、函数调用、Pydantic 输出或其他结构化抽取组件。
