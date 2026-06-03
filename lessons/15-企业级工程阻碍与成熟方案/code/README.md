# 代码说明

`enterprise_update_patterns.cypher` 展示企业知识图谱最常见的工程模式：

- 用稳定主键做 upsert。
- 用内容 hash 判断是否需要重新抽取。
- 用 `validTo` 标记关系失效，而不是直接物理删除。
- 删除文档时避免误删共享实体。
- 多跳查询限制 hop 数，避免路径爆炸。
