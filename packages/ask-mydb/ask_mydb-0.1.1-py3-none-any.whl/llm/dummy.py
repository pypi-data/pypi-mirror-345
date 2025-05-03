# askdb/llm/dummy.py

from .base import LLMProvider

class DummyLLM(LLMProvider):
    def generate_sql(self, prompt: str, schema: str) -> str:
        # Fake SQL just to test the flow
        return "SELECT * FROM users"
