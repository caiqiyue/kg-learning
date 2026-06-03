"""全局 GraphRAG 检索示例：使用社区摘要回答整体问题。"""

from dataclasses import dataclass


@dataclass
class CommunityHit:
    community_id: str
    title: str
    summary: str
    score: float
    rank: int


def build_global_context(communities: list[CommunityHit]) -> str:
    """把社区摘要拼成上下文，适合回答“整体主题是什么”。"""
    lines = ["Global community summaries:"]
    for community in sorted(communities, key=lambda item: (item.rank, item.score), reverse=True):
        # rank 表示社区覆盖了多少来源，score 表示和问题的语义相似度。
        lines.append(
            f"- community={community.community_id}, title={community.title}, "
            f"rank={community.rank}, score={community.score}: {community.summary}"
        )
    return "\n".join(lines)


mock_communities = [
    CommunityHit(
        community_id="0-12",
        title="GraphRAG Pipeline",
        summary="This community discusses chunks, entities, vector indexes, and graph-based retrieval.",
        score=0.88,
        rank=5,
    ),
    CommunityHit(
        community_id="0-21",
        title="Neo4j Operations",
        summary="This community focuses on Cypher CRUD, deletion, deduplication, and constraints.",
        score=0.82,
        rank=3,
    ),
]

print(build_global_context(mock_communities))
