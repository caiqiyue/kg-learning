"""混合 GraphRAG 检索与证据拼装示例。

这个脚本不调用真实 embedding 或 LLM，而是完整演示 GraphRAG 检索层应做的事：
1. 从不同入口得到候选证据：向量、全文、图邻域、社区摘要。
2. 按 source_id 去重，保留最高分证据。
3. 按证据类型和分数排序，控制上下文长度。
4. 拼装成 LLM 可读、可引用的中文上下文。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    """一条可交给 LLM 的证据。"""

    source_id: str
    source_type: str
    text: str
    score: float
    citation: str


def vector_retrieve(question: str) -> list[Evidence]:
    """模拟 chunk 向量检索。"""
    return [
        Evidence(
            source_id="chunk:c1",
            source_type="chunk",
            text="GraphRAG 从相似 chunk 出发，再沿实体关系扩展上下文。",
            score=0.91,
            citation="lesson11.md#chunk-1",
        )
    ]


def fulltext_retrieve(question: str) -> list[Evidence]:
    """模拟全文检索，适合命中文件名、术语和编号。"""
    if "Neo4j" not in question and "Cypher" not in question:
        return []
    return [
        Evidence(
            source_id="chunk:c2",
            source_type="chunk",
            text="Neo4j 使用 Cypher 查询图结构，适合回答结构化事实。",
            score=0.84,
            citation="lesson08.md#chunk-2",
        )
    ]


def graph_expand(seed_entities: list[str]) -> list[Evidence]:
    """模拟实体邻域扩展。"""
    facts = {
        "GraphRAG": [
            Evidence(
                source_id="fact:graphrag-uses-neo4j",
                source_type="graph_fact",
                text="GraphRAG - USES - Neo4j",
                score=0.88,
                citation="Neo4j path GraphRAG/USES/Neo4j",
            )
        ],
        "Neo4j": [
            Evidence(
                source_id="fact:neo4j-supports-cypher",
                source_type="graph_fact",
                text="Neo4j - SUPPORTS - Cypher",
                score=0.86,
                citation="Neo4j path Neo4j/SUPPORTS/Cypher",
            )
        ],
    }
    results: list[Evidence] = []
    for entity in seed_entities:
        results.extend(facts.get(entity, []))
    return results


def global_community_retrieve(question: str) -> list[Evidence]:
    """模拟社区摘要检索，适合整体总结类问题。"""
    if "整体" not in question and "总结" not in question:
        return []
    return [
        Evidence(
            source_id="community:0-12",
            source_type="community",
            text="本社区总结了 GraphRAG、Neo4j、Cypher、向量检索和实体邻域扩展的关系。",
            score=0.80,
            citation="community summary 0-12",
        )
    ]


def merge_evidence(groups: list[list[Evidence]], limit: int = 6) -> list[Evidence]:
    """合并多路证据，按 source_id 去重并保留最高分。"""
    by_source: dict[str, Evidence] = {}
    for group in groups:
        for evidence in group:
            old = by_source.get(evidence.source_id)
            if old is None or evidence.score > old.score:
                by_source[evidence.source_id] = evidence

    type_weight = {"graph_fact": 0.03, "chunk": 0.02, "community": 0.01}
    return sorted(
        by_source.values(),
        key=lambda item: item.score + type_weight.get(item.source_type, 0),
        reverse=True,
    )[:limit]


def build_answer_context(evidence_items: list[Evidence]) -> str:
    """拼装 LLM 上下文，并保留 citation 方便回答引用。"""
    lines = ["请只基于以下证据回答问题。每条证据都带有 citation，回答时保留来源。"]
    for index, evidence in enumerate(evidence_items, start=1):
        lines.append(
            f"[{index}] type={evidence.source_type} score={evidence.score:.2f} "
            f"citation={evidence.citation}\n{evidence.text}"
        )
    return "\n\n".join(lines)


def retrieve(question: str) -> str:
    """一个最小但完整的混合 GraphRAG 检索流程。"""
    seed_entities = [
        entity
        for entity in ["GraphRAG", "Neo4j", "Cypher"]
        if entity.lower() in question.lower()
    ]
    evidence_items = merge_evidence(
        [
            vector_retrieve(question),
            fulltext_retrieve(question),
            graph_expand(seed_entities),
            global_community_retrieve(question),
        ]
    )
    return build_answer_context(evidence_items)


if __name__ == "__main__":
    print(retrieve("整体总结 GraphRAG 为什么要结合 Neo4j 和 Cypher？"))
