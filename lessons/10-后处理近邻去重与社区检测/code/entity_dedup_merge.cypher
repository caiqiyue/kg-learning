// 实体去重与合并示例。
// 前置条件：实体节点带有 __Entity__ label，并有 id 和 embedding 属性。

// 1. 找出同 label 下相似的实体候选。
// 注意：这里只是候选，不建议直接自动合并所有结果。
MATCH (n:__Entity__)
WHERE n.embedding IS NOT NULL AND n.id IS NOT NULL
WITH n
MATCH (m:__Entity__)
WHERE elementId(n) < elementId(m)
  AND labels(n) = labels(m)
  AND m.embedding IS NOT NULL
  AND vector.similarity.cosine(n.embedding, m.embedding) > 0.97
RETURN n.id AS entityA,
       m.id AS entityB,
       vector.similarity.cosine(n.embedding, m.embedding) AS score
LIMIT 50;

// 2. 人工确认后再合并。
// $nodeIds 是用户确认可以合并的一组 elementId。
MATCH (n)
WHERE elementId(n) IN $nodeIds
WITH collect(n) AS nodes
CALL apoc.refactor.mergeNodes(
  nodes,
  {
    properties: "discard",
    mergeRels: true,
    produceSelfRel: false
  }
)
YIELD node
RETURN node.id AS mergedEntityId;
