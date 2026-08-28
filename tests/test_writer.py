from types import SimpleNamespace

from agents.writer import Writer


class FakeMessages:
    def create(self, model, max_tokens, messages):
        return SimpleNamespace(content=[SimpleNamespace(type="text", text="final synthesized answer")])


class FakeClaude:
    def __init__(self):
        self.messages = FakeMessages()


def test_writer_produces_answer_from_findings():
    writer = Writer(FakeClaude(), "claude-haiku-4-5")
    state = {
        "question": "What is LangGraph?",
        "findings": "LangGraph is a graph-based orchestration library.",
        "answer": "",
    }

    result = writer.run(state)

    assert result["answer"] == "final synthesized answer"
    assert result["question"] == "What is LangGraph?"
    assert result["findings"] == "LangGraph is a graph-based orchestration library."
