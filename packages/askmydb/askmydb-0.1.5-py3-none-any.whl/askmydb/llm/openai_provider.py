import openai
from openai import OpenAI
from askmydb.llm.base import LLMProvider
from .sql_prompt import build_sql_prompt, build_system_prompt


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, api_key: str, base_url: str = 'https://api.openai.com/v1', model: str = "gpt-3.5-turbo",temperature=0.0):
        """
        Initialize OpenAIProvider with API key and model.
        """
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
    def generate_sql(self, prompt: str, schema: str) -> str:
        """
        Generate SQL query from the given prompt and schema using OpenAI API.
        
        Args:
            prompt (str): The natural language prompt.
            schema (str): The database schema.
        
        Returns:
            str: The generated SQL query.
        """
        try:
            system_prompt = build_system_prompt()
            full_prompt = build_sql_prompt(prompt, schema)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=self.temperature,
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAIProvider.generate_sql error: {e}") from e
