from ollama import Client as OllamaClient


class Writer:
    def __init__(self, ollama_client, model: str):
        self.ollama = ollama_client
        self.model = model

    @classmethod
    def from_config(cls, ollama_base_url: str, ollama_model: str) -> "Writer":
        return cls(OllamaClient(host=ollama_base_url), ollama_model)

    def run(self, state: dict) -> dict:
        question = state["question"]
        findings = state["findings"]

        prompt = (
            f"Question: {question}\n\n"
            f"Research findings:\n{findings}\n\n"
            "Write a clear, direct answer to the question using the findings above."
        )
        response = self.ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
        answer = response["message"]["content"]

        return {**state, "answer": answer}
