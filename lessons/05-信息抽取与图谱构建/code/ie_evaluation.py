"""信息抽取评估示例：计算实体抽取的 precision、recall 和 F1。"""

# gold_entities 表示人工标注的标准答案。
# 在企业项目中，gold set 通常来自专家标注或抽样人工审核。
gold_entities = {
    ("llm-graph-builder", "Project"),
    ("LangChain", "Library"),
    ("PDF", "DocumentType"),
    ("Neo4j", "Database"),
}

# predicted_entities 表示模型或规则抽取出来的结果。
# 这里故意漏掉 PDF，并多抽出一个错误实体 Graph，方便观察指标变化。
predicted_entities = {
    ("llm-graph-builder", "Project"),
    ("LangChain", "Library"),
    ("Neo4j", "Database"),
    ("Graph", "Concept"),
}

# true_positive 是预测正确的实体。
true_positive = gold_entities & predicted_entities

# false_positive 是系统多抽出来但标准答案没有的实体。
false_positive = predicted_entities - gold_entities

# false_negative 是标准答案里有，但系统漏掉的实体。
false_negative = gold_entities - predicted_entities

# precision 关注“抽出来的有多少是真的”。
precision = len(true_positive) / len(predicted_entities)

# recall 关注“应该抽的有多少被抽到了”。
recall = len(true_positive) / len(gold_entities)

# F1 是 precision 和 recall 的调和平均，适合整体比较。
f1 = 2 * precision * recall / (precision + recall)

print("正确抽取:", true_positive)
print("误抽实体:", false_positive)
print("漏抽实体:", false_negative)
print("Precision:", round(precision, 3))
print("Recall:", round(recall, 3))
print("F1:", round(f1, 3))
