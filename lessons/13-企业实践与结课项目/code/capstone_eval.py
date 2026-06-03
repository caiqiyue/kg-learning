"""零售知识中台评估示例：同时看抽取、诊断、反馈和成本。"""

metrics = {
    "entity_precision": 0.91,
    "entity_recall": 0.83,
    "relationship_precision": 0.78,
    "answer_groundedness": 0.86,
    "source_citation_rate": 0.94,
    "diagnosis_hit_rate": 0.72,
    "feedback_fix_days": 3.5,
    "avg_latency_seconds": 3.8,
    "avg_tokens_per_document": 4200,
}


def grade_knowledge_hub(metrics: dict) -> str:
    """根据多个维度给零售知识中台一个简单评级。"""
    if metrics["answer_groundedness"] < 0.8:
        return "需要优先改进答案引用和事实约束"
    if metrics["relationship_precision"] < 0.75:
        return "需要优先改进关系抽取和 schema 约束"
    if metrics["diagnosis_hit_rate"] < 0.7:
        return "需要优先改进诊断链路和业务规则图谱"
    if metrics["feedback_fix_days"] > 5:
        return "需要缩短反馈审核和知识更新周期"
    if metrics["avg_latency_seconds"] > 5:
        return "需要优化检索链路和索引"
    return "达到零售知识中台企业级原型要求"


print(grade_knowledge_hub(metrics))
