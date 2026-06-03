"""最小版文档到知识图谱流水线，用内存数据模拟 Neo4j 写入。"""

import hashlib


document = {
    "fileName": "demo.txt",
    "text": "Neo4j LLM Graph Builder uses LangChain. LangChain calls LLMGraphTransformer.",
}


def chunk_text(text: str, size: int = 45) -> list[str]:
    """真实项目按 token 切分；这里用字符长度模拟，方便理解流程。"""
    return [text[i:i + size] for i in range(0, len(text), size)]


def chunk_id(text: str) -> str:
    """使用内容 hash 做 chunk id，重试时同一文本会得到同一 id。"""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def mock_extract(chunk: str) -> dict:
    """模拟 LLM 抽取结果。真实项目会调用 LLMGraphTransformer。"""
    nodes = []
    rels = []
    if "Neo4j" in chunk:
        nodes.append(("Project", "Neo4j LLM Graph Builder"))
        nodes.append(("Library", "LangChain"))
        rels.append(("Neo4j LLM Graph Builder", "USES", "LangChain"))
    if "LLMGraphTransformer" in chunk:
        nodes.append(("Library", "LangChain"))
        nodes.append(("Tool", "LLMGraphTransformer"))
        rels.append(("LangChain", "CALLS", "LLMGraphTransformer"))
    return {"nodes": nodes, "relationships": rels}


# graph 用内存字典模拟 Neo4j，方便不装数据库也能理解数据结构。
graph = {"documents": [], "chunks": [], "entities": set(), "relationships": []}
graph["documents"].append({"fileName": document["fileName"], "status": "Processing"})

previous_id = None
for position, text in enumerate(chunk_text(document["text"]), start=1):
    # 每个 chunk 使用内容 hash 作为稳定 id，重试时不会重复创建。
    cid = chunk_id(text)
    graph["chunks"].append({"id": cid, "text": text, "position": position})
    # PART_OF 表示 chunk 属于哪个文档，是回答引用来源的关键关系。
    graph["relationships"].append((cid, "PART_OF", document["fileName"]))
    if previous_id:
        # NEXT_CHUNK 保留原文顺序，方便检索时扩展前后文。
        graph["relationships"].append((previous_id, "NEXT_CHUNK", cid))
    previous_id = cid

    # mock_extract 模拟 LLMGraphTransformer 的实体/关系抽取结果。
    extracted = mock_extract(text)
    for label, entity_id in extracted["nodes"]:
        graph["entities"].add((label, entity_id))
        # HAS_ENTITY 把文本证据和结构化实体连起来，是 GraphRAG 溯源的核心。
        graph["relationships"].append((cid, "HAS_ENTITY", entity_id))
    graph["relationships"].extend(extracted["relationships"])

graph["documents"][0]["status"] = "Completed"
print(graph)
