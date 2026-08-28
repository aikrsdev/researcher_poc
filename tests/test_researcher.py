from agents.researcher import Researcher


class FakeTavily:
    def search(self, query):
        return {"results": [{"url": "http://example.com", "content": "Example info"}]}


class FakeOllama:
    def chat(self, model, messages):
        return {"message": {"content": "condensed findings"}}


class FailingTavily:
    def search(self, query):
        raise RuntimeError("search failed")


def test_researcher_populates_findings_and_search_results():
    researcher = Researcher(FakeTavily(), FakeOllama(), "llama3.2")
    state = {"question": "What is LangGraph?", "search_results": [], "findings": "", "answer": ""}

    result = researcher.run(state)

    assert result["findings"] == "condensed findings"
    assert result["search_results"] == [{"url": "http://example.com", "content": "Example info"}]
    assert result["question"] == "What is LangGraph?"


def test_researcher_degrades_gracefully_on_search_failure():
    researcher = Researcher(FailingTavily(), FakeOllama(), "llama3.2")
    state = {"question": "q", "search_results": [], "findings": "", "answer": ""}

    result = researcher.run(state)

    assert result["search_results"] == []
    assert "failed" in result["findings"].lower()
