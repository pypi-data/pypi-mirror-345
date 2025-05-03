
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    
    """
    Abstract base class for LLM providers.
    """
    
    @abstractmethod
    def generate_sql(self, prompt: str, schema:str) -> str:
        """
        Generate SQL query from the given prompt and schema.
        
        Args:
            prompt (str): The natural language prompt.
            schema (str): The database schema.
        
        Returns:
            str: The generated SQL query.
        """
        pass
    