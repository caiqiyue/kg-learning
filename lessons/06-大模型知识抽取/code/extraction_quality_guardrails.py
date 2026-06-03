"""LLM 知识抽取质量护栏示例。

生产系统里，LLM 输出不能直接写入主图谱。
通常要先经过 schema、置信度、来源、重复实体和高风险关系检查。
"""

ALLOWED_NODE_LABELS = {"Metric", "Symptom", "Cause", "Action", "Rule", "Evidence"}
ALLOWED_RELATIONSHIP_TYPES = {"INDICATES", "MAY_BE_CAUSED_BY", "RECOMMENDS", "SUPPORTED_BY"}
HIGH_RISK_RELATIONSHIPS = {"RECOMMENDS"}


def validate_extraction(result: dict) -> list[str]:
    """返回问题列表；空列表表示可以进入下一步写库。"""
    issues = []
    node_ids = {node["id"] for node in result.get("nodes", [])}

    for node in result.get("nodes", []):
        if node.get("label") not in ALLOWED_NODE_LABELS:
            issues.append(f"节点 {node.get('id')} 的类型不在白名单中")
        if not node.get("source_chunk_id"):
            issues.append(f"节点 {node.get('id')} 缺少来源 chunk")

    for rel in result.get("relationships", []):
        if rel.get("type") not in ALLOWED_RELATIONSHIP_TYPES:
            issues.append(f"关系 {rel.get('type')} 不在白名单中")
        if rel.get("source_id") not in node_ids or rel.get("target_id") not in node_ids:
            issues.append(f"关系 {rel} 引用了本次抽取中不存在的节点")
        if rel.get("confidence", 0) < 0.7:
            issues.append(f"关系 {rel.get('type')} 置信度过低")
        if rel.get("type") in HIGH_RISK_RELATIONSHIPS and not rel.get("evidence_text"):
            issues.append("高风险推荐关系必须带原文证据")

    return issues


sample = {
    "nodes": [
        {"id": "conversion_rate", "label": "Metric", "source_chunk_id": "c1"},
        {"id": "discount_action", "label": "Action", "source_chunk_id": "c1"},
    ],
    "relationships": [
        {
            "source_id": "conversion_rate",
            "type": "RECOMMENDS",
            "target_id": "discount_action",
            "confidence": 0.64,
            "evidence_text": "",
        }
    ],
}

print("质量问题:")
for issue in validate_extraction(sample):
    print("-", issue)
