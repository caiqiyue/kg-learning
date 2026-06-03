# 03 资源描述框架、本体语言与三元组

## 引言

如果 Neo4j 属性图更像工程数据库，那么 RDF/OWL 更像知识表达标准。它们来自语义网传统，目标是让不同系统能用统一方式表达和交换知识。

## 三元组

RDF 的核心是三元组：

```text
subject predicate object
```

例如：

```text
Neo4j supports Cypher
GraphRAG uses KnowledgeGraph
Chunk hasEntity Entity
```

三元组看起来简单，但它提供了一种通用语言：任何事实都可以拆成“谁和谁有什么关系”。大量三元组连接起来，就形成语义图。

## 本体是什么

本体可以理解为“领域概念说明书”。它定义：

- 有哪些类，例如 `Person`、`Company`、`Document`。
- 有哪些关系，例如 `WORKS_AT`、`PART_OF`、`HAS_ENTITY`。
- 哪些属性是必须的，例如实体必须有 `id`。
- 哪些关系允许连接哪些类型，例如 `Chunk HAS_ENTITY Entity`。

如果没有本体或 schema，LLM 可能一会儿抽出 `Company`，一会儿抽出 `Organization`，一会儿又抽出 `Org`。这些都可能指同一类概念，但会让图谱变脏。

## RDF 和 OWL 的区别

可以用“菜单”和“餐厅规则”来理解。

RDF 像菜单上的一条条事实：

```text
宫保鸡丁 - 属于 - 川菜
川菜 - 口味 - 辣
```

OWL 更像餐厅背后的规则：

```text
川菜 是 菜系 的一种
每道菜 至少属于 一个菜系
如果某道菜属于川菜，那么它也是中餐
```

RDF 更偏“表达事实”，OWL 更偏“定义概念、约束和推理规则”。Neo4j 属性图则更偏“工程查询和应用开发”。三者不是谁替代谁，而是关注点不同。

## RDF/OWL 与 Neo4j 的关系

RDF/OWL 强调标准化语义、推理和跨系统互操作。Neo4j 属性图强调工程查询、可视化、路径遍历和应用开发。企业中两者可以并存：

- 用 RDF/OWL 做标准、定义和交换。
- 用 Neo4j 做应用图谱、GraphRAG 和实时查询。

## 和 LLM 的关系

LLM 让三元组抽取变容易了，但也让 schema 控制更重要。没有约束的大模型会创造看似合理但不可维护的节点和关系。课程后续会看到，本项目通过 `allowedNodes` 和 `allowedRelationship` 控制抽取范围。

## 小结

三元组是知识图谱的最小事实单位，本体是事实的组织规则。一个成熟图谱系统既要允许知识生长，也要有足够清晰的 schema 防止混乱。
