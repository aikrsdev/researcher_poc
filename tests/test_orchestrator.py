from orchestrator import build_graph


class StubResearcher:
    def run(self, state):
        return {**state, "search_results": [], "findings": "stub findings"}


class StubWriter:
    def run(self, state):
        assert state["findings"] == "stub findings"
        return {**state, "answer": "stub answer"}


def test_graph_runs_researcher_then_writer():
    graph = build_graph(StubResearcher(), StubWriter())

    result = graph.invoke({"question": "q", "search_results": [], "findings": "", "answer": ""})

    assert result["findings"] == "stub findings"
    assert result["answer"] == "stub answer"
