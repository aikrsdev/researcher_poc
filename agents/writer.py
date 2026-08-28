import logging

import anthropic

logger = logging.getLogger(__name__)


class Writer:
    def __init__(self, claude_client, model: str):
        self.claude = claude_client
        self.model = model

    @classmethod
    def from_config(cls, claude_model: str) -> "Writer":
        return cls(anthropic.Anthropic(), claude_model)

    def run(self, state: dict) -> dict:
        question = state["question"]
        findings = state["findings"]

        logger.info("writer: synthesizing answer for question=%r", question)

        prompt = (
            f"Question: {question}\n\n"
            f"Research findings:\n{findings}\n\n"
            "Write a clear, direct answer to the question using the findings above."
        )
        response = self.claude.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = next((b.text for b in response.content if b.type == "text"), "")

        logger.info("writer: answer ready (%d chars)", len(answer))

        return {**state, "answer": answer}
