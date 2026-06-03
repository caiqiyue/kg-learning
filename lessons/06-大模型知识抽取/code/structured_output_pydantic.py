"""Pydantic 结构化输出示例：把 LLM 抽取结果约束成可校验对象。

这个例子不调用真实大模型，重点展示 schema 应该如何设计。
真实系统可以把这些 Pydantic 模型交给支持结构化输出的 LLM SDK。
"""

from pydantic import BaseModel, Field, ValidationError, field_validator


class ExtractedNode(BaseModel):
    """图谱节点：实体 id、类型、名称和来源 chunk。"""

    id: str = Field(description="实体稳定 id，例如 conversion_rate")
    label: str = Field(description="实体类型，例如 Metric、Cause、Action")
    name: str = Field(description="实体中文名称")
    source_chunk_id: str = Field(description="实体来自哪个 chunk")

    @field_validator("label")
    @classmethod
    def label_must_be_allowed(cls, value: str) -> str:
        """限制节点类型，防止模型创造大量相似 label。"""
        allowed = {"Metric", "Symptom", "Cause", "Action", "Rule", "Evidence"}
        if value not in allowed:
            raise ValueError(f"不允许的节点类型: {value}")
        return value


class ExtractedRelationship(BaseModel):
    """图谱关系：必须包含起点、关系类型、终点、置信度和来源。"""

    source_id: str
    type: str
    target_id: str
    confidence: float = Field(ge=0, le=1)
    evidence_text: str

    @field_validator("type")
    @classmethod
    def relationship_must_be_allowed(cls, value: str) -> str:
        """限制关系类型，防止关系命名漂移。"""
        allowed = {"INDICATES", "MAY_BE_CAUSED_BY", "RECOMMENDS", "SUPPORTED_BY"}
        if value not in allowed:
            raise ValueError(f"不允许的关系类型: {value}")
        return value


class GraphExtraction(BaseModel):
    """一次 chunk 抽取结果。"""

    nodes: list[ExtractedNode]
    relationships: list[ExtractedRelationship]


good_payload = {
    "nodes": [
        {"id": "conversion_rate", "label": "Metric", "name": "转化率", "source_chunk_id": "c1"},
        {"id": "low_lead_quality", "label": "Cause", "name": "线索质量偏低", "source_chunk_id": "c1"},
    ],
    "relationships": [
        {
            "source_id": "conversion_rate",
            "type": "MAY_BE_CAUSED_BY",
            "target_id": "low_lead_quality",
            "confidence": 0.86,
            "evidence_text": "转化率下降可能与线索质量偏低有关。",
        }
    ],
}

bad_payload = {
    "nodes": [
        {"id": "conversion_rate", "label": "BusinessThing", "name": "转化率", "source_chunk_id": "c1"},
    ],
    "relationships": [],
}

print("好结果:", GraphExtraction.model_validate(good_payload))

try:
    GraphExtraction.model_validate(bad_payload)
except ValidationError as error:
    print("坏结果被拦截:")
    print(error)
