// Neo4j GDS 社区检测示例。
// 前置条件：安装 Graph Data Science，并且图中已有实体之间的关系。

// 1. 如果同名投影已存在，先删除，避免投影过期。
CALL gds.graph.drop('entity-communities', false) YIELD graphName;

// 2. 投影实体图；这里排除 Document、Chunk 和 __Community__。
MATCH (source:__Entity__)-[r]-(target:__Entity__)
WITH gds.graph.project(
  'entity-communities',
  source,
  target,
  {},
  {undirectedRelationshipTypes: ['*']}
) AS g
RETURN g.graphName AS graphName,
       g.nodeCount AS nodeCount,
       g.relationshipCount AS relationshipCount;

// 3. 使用 Leiden 写入社区编号。
CALL gds.leiden.write(
  'entity-communities',
  {
    writeProperty: 'communityId',
    includeIntermediateCommunities: true
  }
)
YIELD communityCount, modularity
RETURN communityCount, modularity;

// 4. 根据 communityId 创建 __Community__ 节点。
MATCH (e:__Entity__)
WHERE e.communityId IS NOT NULL
MERGE (c:__Community__ {id: toString(e.communityId)})
MERGE (e)-[:IN_COMMUNITY]->(c);
