// 销售诊断知识中台最小种子图谱。
// 用它演示 Metric、Symptom、Cause、Action、Rule、Evidence 与 Feedback 的关系。

MERGE (doc:Document {id: "sales-diagnosis-playbook-001"})
SET doc.title = "销售转化率诊断手册",
    doc.sourceType = "playbook",
    doc.updatedAt = datetime("2026-06-01T10:00:00");

MERGE (chunk:Chunk {id: "sales-diagnosis-playbook-001-c1"})
SET chunk.text = "当销售转化率下降时，应优先检查线索质量、销售跟进时效、产品匹配度和合规约束。",
    chunk.position = 1
MERGE (chunk)-[:PART_OF]->(doc);

MERGE (metric:Metric {id: "conversion_rate", name: "销售转化率"})
SET metric.definition = "成交客户数 / 有效销售机会数";

MERGE (symptom:Symptom {id: "conversion_rate_drop", name: "销售转化率下降"})
MERGE (cause1:Cause {id: "low_lead_quality", name: "线索质量偏低"})
MERGE (cause2:Cause {id: "slow_follow_up", name: "销售跟进不及时"})
MERGE (action1:Action {id: "prioritize_high_score_leads", name: "优先跟进高评分线索"})
MERGE (action2:Action {id: "follow_up_within_24h", name: "24 小时内完成首次跟进"})
MERGE (rule:Rule {id: "rule_conversion_diagnosis_v1", name: "转化率下降诊断规则", version: "v1"})
SET rule.validFrom = date("2026-06-01"),
    rule.validTo = date("2026-12-31");

MERGE (constraint:Constraint {id: "compliance_contact_limit", name: "客户触达合规限制"})
MERGE (feedback:Feedback {id: "feedback-001", feedbackType: "diagnosis_correction", status: "pending_review"})
SET feedback.comment = "部分地区转化率下降并不是线索质量问题，而是销售人力不足。";

MERGE (metric)-[:INDICATES]->(symptom)
MERGE (symptom)-[:MAY_BE_CAUSED_BY]->(cause1)
MERGE (symptom)-[:MAY_BE_CAUSED_BY]->(cause2)
MERGE (cause1)-[:RECOMMENDS]->(action1)
MERGE (cause2)-[:RECOMMENDS]->(action2)
MERGE (action2)-[:CONSTRAINED_BY]->(constraint)
MERGE (rule)-[:DIAGNOSES]->(symptom)
MERGE (rule)-[:CHECKS]->(cause1)
MERGE (rule)-[:CHECKS]->(cause2)
MERGE (chunk)-[:SUPPORTS_FACT]->(rule)
MERGE (feedback)-[:TARGETS]->(rule);
