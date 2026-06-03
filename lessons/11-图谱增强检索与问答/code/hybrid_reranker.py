"""GraphRAG 混合检索重排示例。

生产系统常把向量分数、全文命中、图距离、来源可信度组合起来排序。
这个例子用简单公式帮助理解，不依赖外部库。
"""

from dataclasses import dataclass


@dataclass
class CandidateContext:
    chunk_id: str
    text: str
    vector_score: float
    keyword_score: float
    graph_distance: int
    source_trust: float
    has_citation: bool


def score_candidate(candidate: CandidateContext) -> float:
    """把不同检索信号合成一个排序分数。"""
    graph_bonus = max(0, 1 - 0.2 * candidate.graph_distance)
    citation_bonus = 0.1 if candidate.has_citation else -0.2
    return (
        0.40 * candidate.vector_score
        + 0.25 * candidate.keyword_score
        + 0.20 * graph_bonus
        + 0.15 * candidate.source_trust
        + citation_bonus
    )


def rerank(candidates: list[CandidateContext], limit: int = 5) -> list[CandidateContext]:
    """按综合分数重排候选上下文。"""
    return sorted(candidates, key=score_candidate, reverse=True)[:limit]


candidates = [
    CandidateContext("c1", "转化率下降可能与线索质量有关", 0.88, 0.7, 2, 0.9, True),
    CandidateContext("c2", "销售流程优化建议", 0.91, 0.2, 4, 0.6, False),
    CandidateContext("c3", "24 小时内首次跟进提升成交率", 0.79, 0.8, 1, 0.85, True),
]

for item in rerank(candidates):
    print(item.chunk_id, round(score_candidate(item), 3), item.text)
