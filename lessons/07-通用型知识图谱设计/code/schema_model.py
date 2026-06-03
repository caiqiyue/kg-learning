"""用 Python 数据结构描述一个通用型知识图谱 schema。"""

# 节点 schema 描述每类节点的主键和核心属性。
# 真实工程中，这些定义可以写进配置文件，再被抽取器和校验器共同使用。
NODE_SCHEMA = {
    "Document": {
        "primary_key": "fileName",
        "required_properties": ["fileName", "status", "updatedAt"],
        "description": "表示一个被处理的数据源，例如 PDF、网页或视频。",
    },
    "Chunk": {
        "primary_key": "id",
        "required_properties": ["id", "text", "position"],
        "description": "表示文档切分后的文本片段，用于检索和溯源。",
    },
    "__Entity__": {
        "primary_key": "id",
        "required_properties": ["id"],
        "description": "表示 LLM 或规则抽取出的业务实体。",
    },
    "__Community__": {
        "primary_key": "id",
        "required_properties": ["id", "level"],
        "description": "表示图算法发现的实体社区，用于全局 GraphRAG。",
    },
}

# 关系 schema 描述允许的起点、关系类型和终点。
# 这样可以防止 LLM 随意创造不可维护的关系。
RELATIONSHIP_SCHEMA = [
    {"start": "Chunk", "type": "PART_OF", "end": "Document"},
    {"start": "Document", "type": "FIRST_CHUNK", "end": "Chunk"},
    {"start": "Chunk", "type": "NEXT_CHUNK", "end": "Chunk"},
    {"start": "Chunk", "type": "HAS_ENTITY", "end": "__Entity__"},
    {"start": "__Entity__", "type": "IN_COMMUNITY", "end": "__Community__"},
    {"start": "__Community__", "type": "PARENT_COMMUNITY", "end": "__Community__"},
]


def explain_schema() -> None:
    """打印 schema，帮助学习者观察通用型图谱的稳定骨架。"""
    print("节点类型:")
    for label, config in NODE_SCHEMA.items():
        print(f"- {label}: 主键={config['primary_key']}，说明={config['description']}")

    print("\n允许关系:")
    for rel in RELATIONSHIP_SCHEMA:
        print(f"- ({rel['start']})-[:{rel['type']}]->({rel['end']})")


explain_schema()
