# 05 信息抽取：从规则、深度学习到图谱构建

## 引言

知识图谱不会凭空出现。它通常来自结构化数据库、业务系统日志、网页、论文、合同、客服记录等材料。把这些材料变成图谱，需要信息抽取。

## 典型流水线

一条传统知识抽取流水线包括：

1. **文本清洗**：去掉噪声、HTML、页眉页脚、乱码。
2. **分句与分块**：把长文本切成模型可处理的片段。
3. **实体抽取**：识别人名、机构、产品、地点、概念。
4. **关系抽取**：判断实体之间是否存在关系。
5. **实体链接**：把“OpenAI”“Open AI”“OpenAI 公司”归到同一实体。
6. **共指消解**：判断“它”“该公司”“苹果”分别指谁。
7. **入库与校验**：写入图数据库并检查质量。

## 一句原文怎么变成图谱

原文：

```text
知识图谱构建器 使用 LangChain 从 PDF 文档中抽取实体，并把结果写入 Neo4j。
```

可以抽出：

- 实体：`知识图谱构建器`、`LangChain`、`PDF`、`Neo4j`
- 关系：`知识图谱构建器 - USES - LangChain`
- 关系：`知识图谱构建器 - EXTRACTS_FROM - PDF`
- 关系：`知识图谱构建器 - STORES_IN - Neo4j`

如果原文后面又说“它还支持网页”，共指消解要判断“它”指的是 `知识图谱构建器`，不是 `Neo4j` 数据库。

## 从规则到深度学习

早期方法常用规则、词典、正则表达式和依存句法。它们可控，但覆盖率有限。

深度学习以后，NER 常用 BiLSTM-CRF、Transformer、BERT 类模型；关系抽取使用分类模型、序列标注模型、生成式模型。这些方法泛化更好，但需要训练数据和评估集。

LLM 时代，抽取变成“给出 schema，让模型直接输出结构化节点和关系”。这降低了启动成本，但引入新问题：幻觉、重复实体、关系命名漂移、长文档上下文丢失。

## 评估指标

抽取系统至少要看：

- 实体准确率：抽出来的是不是真的实体？
- 实体召回率：重要实体漏掉多少？
- 关系准确率：关系方向和类型是否正确？
- 溯源完整性：每个事实能否回到原文 chunk？
- 图谱可维护性：schema 是否稳定，重复实体是否可控？

## 代码案例：规则抽取与 F1 评估

下面这个极简案例故意不用复杂模型，用来说明“抽取结果必须能被评估”。真实工程里可以把 `extract` 换成 NER、关系抽取模型或 LLM 结构化输出，但评估逻辑仍然需要保留。

```python
import re

text = "知识图谱构建器 使用 LangChain 从 PDF 文档中抽取实体，并把结果写入 Neo4j。"
gold_entities = {"知识图谱构建器", "LangChain", "PDF", "Neo4j"}

def extract_entities(sentence):
    patterns = [r"知识图谱构建器", r"LangChain", r"PDF", r"Neo4j"]
    return {match for pattern in patterns for match in re.findall(pattern, sentence)}

pred_entities = extract_entities(text)
tp = len(pred_entities & gold_entities)
precision = tp / len(pred_entities) if pred_entities else 0
recall = tp / len(gold_entities) if gold_entities else 0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0

print({"precision": precision, "recall": recall, "f1": f1})
```

这个案例和本课主题匹配：第 05 课重点不是图数据库写入，而是让学习者明白实体、关系、共指、链接和质量评估如何组成抽取闭环。

## 小结

信息抽取不是“模型调用一次”。它是一条数据工程、NLP、图数据库和质量治理共同组成的流水线。LLM 可以让抽取更快启动，但不能替代 schema、评估和后处理。
