// Capstone 最小种子图谱。
// 用它可以快速演示 Document -> Chunk -> Entity -> Community。

MERGE (d:Document {fileName: "capstone-demo.md"})
SET d.status = "Completed";

MERGE (c1:Chunk {id: "capstone-c1"})
SET c1.text = "Neo4j and LangChain can be used to build GraphRAG applications.",
    c1.position = 1
MERGE (c1)-[:PART_OF]->(d);

MERGE (neo4j:__Entity__:Database {id: "Neo4j"})
MERGE (langchain:__Entity__:Library {id: "LangChain"})
MERGE (graphrag:__Entity__:Method {id: "GraphRAG"})

MERGE (c1)-[:HAS_ENTITY]->(neo4j)
MERGE (c1)-[:HAS_ENTITY]->(langchain)
MERGE (c1)-[:HAS_ENTITY]->(graphrag)
MERGE (graphrag)-[:USES]->(neo4j)
MERGE (graphrag)-[:USES]->(langchain);
