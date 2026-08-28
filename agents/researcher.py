from tavily import TavilyClient
from ollama import Client as OllamaClient


class Researcher:
    def __init__(self, tavily_client, ollama_client, model: str):
        self.tavily = tavily_client
        self.ollama = ollama_client
        self.model = model

    @classmethod
    def from_config(cls, tavily_api_key: str, ollama_base_url: str, ollama_model: str) -> "Researcher":
        return cls(
            TavilyClient(api_key=tavily_api_key),
            OllamaClient(host=ollama_base_url),
            ollama_model,
        )

    def run(self, state: dict) -> dict:
        question = state["question"]

        try:
            search_response = self.tavily.search(query=question)
            results = search_response.get("results", [])
        except Exception:
            return {
                **state,
                "search_results": [],
                "findings": "Web search failed; answering from model knowledge only.",
            }

        results_text = "\n\n".join(
            f"Source: {r.get('url')}\n{r.get('content', '')}" for r in results
        )
        prompt = (
            f"Question: {question}\n\n"
            f"Search results:\n{results_text}\n\n"
            "Summarize the key findings relevant to the question. "
            "Keep source URLs alongside the facts they support."
        )
        response = self.ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
        findings = response["message"]["content"]

        return {**state, "search_results": results, "findings": findings}
