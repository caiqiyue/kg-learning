"""根据问题类型选择 GraphRAG 检索模式。"""


def choose_mode(question: str) -> str:
    """用简单规则模拟真实系统的 query router。"""
    q = question.lower()
    # 全局总结类问题更适合走社区摘要，而不是只看某个 chunk。
    if "整体" in question or "总结" in question or "themes" in q:
        return "global_vector"
    # 关系、路径、关联类问题需要沿图结构扩展上下文。
    if "关系" in question or "路径" in question or "怎么关联" in question:
        return "graph_vector_fulltext"
    # 文件名、编号、专有名词通常需要全文检索保证精确命中。
    if "精确" in question or "文件名" in question or "编号" in question:
        return "fulltext"
    # 计数、过滤、结构化统计问题更适合查询语言。
    if "cypher" in q or "多少个" in question:
        return "graph"
    # 默认走向量检索，适合一般语义问答。
    return "vector"


questions = [
    "这批文档整体讲了什么主题？",
    "Neo4j 和 LangChain 怎么关联？",
    "查找文件名 demo.pdf 里的实体",
    "图里有多少个 Document 节点？",
    "知识图谱为什么能帮助 RAG？",
]

for question in questions:
    print(question, "->", choose_mode(question))
