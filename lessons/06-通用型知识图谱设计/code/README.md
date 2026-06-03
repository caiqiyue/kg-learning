# 代码说明

运行：

```bash
python schema_model.py
```

在 Neo4j Browser 中执行：

```cypher
:source schema_constraints.cypher
```

重点：

- `schema_model.py` 用工程配置解释通用型图谱的稳定骨架。
- `schema_constraints.cypher` 展示唯一约束、全文索引和向量索引。
