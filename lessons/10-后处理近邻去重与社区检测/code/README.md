# 代码说明

这些 Cypher 片段是知识图谱后处理思路的简化版。

练习：

1. 先建立 `vector` 索引并给 chunk 写 embedding。
2. 运行 KNN 写入 `SIMILAR`。
3. 观察 `SIMILAR` 是否改善检索扩展。
4. 列出孤立实体，讨论哪些应该删除，哪些应该保留。
