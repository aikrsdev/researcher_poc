from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class GraphState(TypedDict):
    question: str
    search_results: list
    findings: str
    answer: str


def build_graph(researcher, writer):
    graph = StateGraph(GraphState)
    graph.add_node("researcher", researcher.run)
    graph.add_node("writer", writer.run)
    graph.add_edge(START, "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", END)
    return graph.compile()
