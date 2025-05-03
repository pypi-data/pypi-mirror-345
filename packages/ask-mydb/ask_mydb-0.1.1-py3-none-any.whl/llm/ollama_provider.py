import json
import ollama
from .sql_prompt import build_sql_prompt, build_system_prompt
from askmydb.llm.base import LLMProvider

class OllamaProvider(LLMProvider):
    """Ollama AI model provider."""
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3", temperature: float = 0.0):
        try:
            self.base_url = base_url
            self.model = model
            self.temperature = temperature
        except Exception as e:
            raise RuntimeError(f"OllamaProvider.__init__ error: {e}") from e

    def generate_sql(self, prompt: str, schema: str) -> str:
        """
        Generate SQL query from the given prompt and schema using Ollama API.
        """
        try:
            full_prompt = build_sql_prompt(prompt, schema)
            system_prompt = build_system_prompt()

            client = ollama.Client(host=self.base_url)
            response = client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt},
                ],
                format={
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string"
                        }
                    },
                    "required": ["sql"]
                },
                options={
                    "temperature":self.temperature,
                }
            )
            
            # print(f"Response: {json.loads(response['message']['content'])['sql']}")

            return json.loads(response['message']['content'])["sql"]
        except Exception as e:
            raise RuntimeError(f"OllamaProvider.generate_sql error: {e}") from e
