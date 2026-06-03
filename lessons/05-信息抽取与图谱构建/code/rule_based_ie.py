"""规则版信息抽取示例：不用模型，先理解实体、关系和规范化。"""

import re

# 准备一段短文本，模拟真实项目中的一个 chunk。
# 真实系统里，这段文本可能来自 PDF、网页、YouTube 字幕或客服工单。
TEXT = "Neo4j LLM Graph Builder 使用 LangChain 从 PDF 文档中抽取实体，并把结果写入 Neo4j。"

# 定义一个小词典，用来模拟“实体识别”。
# key 是原文中可能出现的写法，value 是统一后的实体 id 和实体类型。
ENTITY_DICTIONARY = {
    "Neo4j LLM Graph Builder": {"id": "llm-graph-builder", "type": "Project"},
    "LangChain": {"id": "LangChain", "type": "Library"},
    "PDF": {"id": "PDF", "type": "DocumentType"},
    "Neo4j": {"id": "Neo4j", "type": "Database"},
}


def extract_entities(text: str) -> list[dict]:
    """用词典匹配实体，并返回统一后的实体结构。"""
    entities = []
    for surface, normalized in ENTITY_DICTIONARY.items():
        # re.escape 可以避免实体名里的特殊字符被当成正则语法。
        if re.search(re.escape(surface), text):
            entities.append({
                "surface": surface,
                "id": normalized["id"],
                "type": normalized["type"],
            })
    return entities


def extract_relationships(text: str, entities: list[dict]) -> list[dict]:
    """用简单规则抽取关系，帮助理解关系抽取的基本思想。"""
    entity_ids = {entity["id"] for entity in entities}
    relationships = []

    # 如果文本同时出现项目和 LangChain，并出现“使用”，就抽取 USES 关系。
    if "llm-graph-builder" in entity_ids and "LangChain" in entity_ids and "使用" in text:
        relationships.append({
            "source": "llm-graph-builder",
            "type": "USES",
            "target": "LangChain",
            "evidence": "文本中出现“使用 LangChain”",
        })

    # 如果文本同时出现项目和 PDF，并出现“抽取”，就抽取 EXTRACTS_FROM 关系。
    if "llm-graph-builder" in entity_ids and "PDF" in entity_ids and "抽取" in text:
        relationships.append({
            "source": "llm-graph-builder",
            "type": "EXTRACTS_FROM",
            "target": "PDF",
            "evidence": "文本中出现“从 PDF 文档中抽取”",
        })

    # 如果文本同时出现项目和 Neo4j，并出现“写入”，就抽取 STORES_IN 关系。
    if "llm-graph-builder" in entity_ids and "Neo4j" in entity_ids and "写入" in text:
        relationships.append({
            "source": "llm-graph-builder",
            "type": "STORES_IN",
            "target": "Neo4j",
            "evidence": "文本中出现“写入 Neo4j”",
        })

    return relationships


entities = extract_entities(TEXT)
relationships = extract_relationships(TEXT, entities)

print("原文:", TEXT)
print("实体:", entities)
print("关系:", relationships)
