"""局部 GraphRAG 检索示例：向量命中 chunk 后扩展实体邻域。"""

from dataclasses import dataclass


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    score: float
    source: str
    entities: list[str]
    neighbor_facts: list[str]


def build_local_context(chunks: list[RetrievedChunk]) -> str:
    """把 chunk、实体和邻域事实拼成 LLM 可读上下文。"""
    blocks = []
    for chunk in sorted(chunks, key=lambda item: item.score, reverse=True):
        # 每个块都保留 source，回答时才能引用来源。
        block = [
            "Document start",
            f"source: {chunk.source}",
            f"chunk_id: {chunk.chunk_id}",
            f"similarity_score: {chunk.score}",
            f"text: {chunk.text}",
            f"entities: {', '.join(chunk.entities)}",
            "neighbor_facts:",
        ]
        block.extend([f"- {fact}" for fact in chunk.neighbor_facts])
        block.append("Document end")
        blocks.append("\n".join(block))
    return "\n\n".join(blocks)


mock_chunks = [
    RetrievedChunk(
        chunk_id="c1",
        text="Neo4j LLM Graph Builder uses LangChain to extract entities.",
        score=0.91,
        source="project README",
        entities=["Neo4j LLM Graph Builder", "LangChain"],
        neighbor_facts=[
            "Neo4j LLM Graph Builder - USES - LangChain",
            "LangChain - CALLS - LLMGraphTransformer",
        ],
    )
]

print(build_local_context(mock_chunks))
