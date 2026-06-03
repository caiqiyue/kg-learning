// 零售知识中台最小种子图谱。
// 用它快速演示 Product、Store、Supplier、Promotion、SalesMetric 与 Rule 的关系。

MERGE (doc:Document {id: "retail-policy-001"})
SET doc.title = "华东区乳制品促销与补货规则",
    doc.sourceType = "operation_policy",
    doc.updatedAt = datetime("2026-06-01T10:00:00");

MERGE (chunk:Chunk {id: "retail-policy-001-c1"})
SET chunk.text = "华东区乳制品促销期间，核心 SKU 库存低于安全库存时，需要优先触发补货。",
    chunk.position = 1
MERGE (chunk)-[:PART_OF]->(doc);

MERGE (milk:Category {id: "cat-dairy", name: "乳制品", level: 2})
MERGE (sku:Product {sku: "SKU-10001", name: "高钙牛奶 250ml", brand: "示例品牌"})
MERGE (store:Store {id: "STORE-SH-001", name: "上海示例门店", city: "上海", region: "华东"})
MERGE (supplier:Supplier {id: "SUP-001", name: "示例乳品供应商", riskLevel: "medium"})
MERGE (promo:Promotion {id: "PROMO-618-DAIRY", name: "618 乳制品促销"})
MERGE (rule:BusinessRule {id: "RULE-REPLENISH-001", name: "促销期安全库存补货规则", version: "v1"})
SET rule.validFrom = date("2026-06-01"),
    rule.validTo = date("2026-06-30");

MERGE (metric:SalesMetric {id: "METRIC-STORE-SKU-20260601"})
SET metric.date = date("2026-06-01"),
    metric.salesAmount = 12800,
    metric.grossMargin = 0.23,
    metric.conversionRate = 0.18;

MERGE (sku)-[:BELONGS_TO]->(milk)
MERGE (sku)-[:SUPPLIED_BY]->(supplier)
MERGE (promo)-[:APPLIES_TO]->(sku)
MERGE (rule)-[:CONSTRAINS]->(promo)
MERGE (metric)-[:MEASURED_FOR]->(sku)
MERGE (metric)-[:MEASURED_AT]->(store)
MERGE (chunk)-[:MENTIONS]->(sku)
MERGE (chunk)-[:SUPPORTS_FACT]->(rule);
