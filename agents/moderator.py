import logging

import anthropic

logger = logging.getLogger(__name__)

FORBIDDEN_SUBJECTS = [
    "violence / weapons instructions",
    "illegal drugs (synthesis, trafficking)",
    "hate speech / discrimination",
    "self-harm / suicide",
    "sexual content involving minors",
    "terrorism / extremism",
    "malware / hacking / cyberattacks",
    "fraud / scams",
    "politics (any topic involving politicians, political parties, elections, "
    "government policy, or political figures — including plain factual or "
    "biographical questions about them)",
]


class Moderator:
    def __init__(self, claude_client, model: str):
        self.claude = claude_client
        self.model = model

    @classmethod
    def from_config(cls, claude_model: str) -> "Moderator":
        return cls(anthropic.Anthropic(), claude_model)

    def check(self, question: str) -> tuple[bool, str]:
        subjects_list = "\n".join(f"- {subject}" for subject in FORBIDDEN_SUBJECTS)
        prompt = (
            "You are a content safety classifier for a Q&A app. Decide whether the "
            "following question is safe to answer. It is UNSAFE if it falls into any "
            f"of these forbidden subjects:\n{subjects_list}\n\n"
            f"Question: {question}\n\n"
            "Respond with exactly one line, either:\n"
            "SAFE\n"
            "or\n"
            "UNSAFE: <short reason>"
        )
        response = self.claude.messages.create(
            model=self.model,
            max_tokens=64,
            messages=[{"role": "user", "content": prompt}],
        )
        text = next((b.text for b in response.content if b.type == "text"), "").strip()

        is_safe = text.upper().startswith("SAFE")
        reason = text.split(":", 1)[1].strip() if ":" in text else "blocked by content policy"

        logger.info("moderator: question=%r verdict=%s", question, "SAFE" if is_safe else "UNSAFE")

        return is_safe, reason
