from agents.writer import Writer


class FakeOllama:
    def chat(self, model, messages):
        return {"message": {"content": "final synthesized answer"}}


def test_writer_produces_answer_from_findings():
    writer = Writer(FakeOllama(), "llama3.2")
    state = {
        "question": "What is LangGraph?",
        "search_results": [],
        "findings": "LangGraph is a graph-based orchestration library.",
        "answer": "",
    }

    result = writer.run(state)

    assert result["answer"] == "final synthesized answer"
    assert result["question"] == "What is LangGraph?"
    assert result["findings"] == "LangGraph is a graph-based orchestration library."
