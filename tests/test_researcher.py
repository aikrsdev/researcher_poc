from types import SimpleNamespace

from agents.researcher import Researcher


class FakeMessages:
    def create(self, model, max_tokens, messages):
        return SimpleNamespace(content=[SimpleNamespace(type="text", text="condensed findings")])


class FakeClaude:
    def __init__(self):
        self.messages = FakeMessages()


def test_researcher_populates_findings_from_model_knowledge():
    researcher = Researcher(FakeClaude(), "claude-haiku-4-5")
    state = {"question": "What is LangGraph?", "findings": "", "answer": ""}

    result = researcher.run(state)

    assert result["findings"] == "condensed findings"
    assert result["question"] == "What is LangGraph?"
