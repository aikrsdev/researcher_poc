import logging

import anthropic

logger = logging.getLogger(__name__)


class Researcher:
    def __init__(self, claude_client, model: str):
        self.claude = claude_client
        self.model = model

    @classmethod
    def from_config(cls, claude_model: str) -> "Researcher":
        return cls(anthropic.Anthropic(), claude_model)

    def run(self, state: dict) -> dict:
        question = state["question"]

        logger.info("researcher: gathering findings for question=%r", question)

        prompt = (
            f"Question: {question}\n\n"
            "Summarize the key facts relevant to this question, from your own knowledge."
        )
        response = self.claude.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        findings = next((b.text for b in response.content if b.type == "text"), "")

        logger.info("researcher: findings ready (%d chars)", len(findings))

        return {**state, "findings": findings}
