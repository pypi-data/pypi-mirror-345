# askmydb

A Python package for querying databases using natural language.

## Overview

askmydb allows you to interact with your databases by asking questions in natural language. It leverages large language models (LLMs) to convert your queries into SQL and execute them on the specified database.

## Features

- Query databases using natural language prompts.
- Supports multiple LLM providers (e.g., dummy, OpenAI, Ollama).
- Works with SQLite and other databases supported by SQLAlchemy.
- Easy to set up and use.

## Installation

Install the package and its dependencies using pip:

```bash
pip install askmydb
```

The package requires the following dependencies:

- openai
- ollama
- sqlalchemy

You can install these dependencies individually if needed:

```bash
pip install openai ollama sqlalchemy
```

## Usage

Below are examples of how to use askmydb with different LLM providers.

### Using OllamaProvider

```python
from askmydb import AskMyDB
from askmydb.llm.ollama_provider import OllamaProvider

if __name__ == "__main__":
    llm = OllamaProvider(base_url="http://localhost:32768", model="qwen2.5:1.5b")
    askDb = AskMyDB(db_url="sqlite:///IMDB.db", llm=llm)
    query, result = askDb.ask("get the movies on action genre with rating more than 5 sort it high to low")
    print(result)
```

### Using OpenAIProvider (via OpenRouter)

```python
from askmydb import AskMyDB
from askmydb.llm.openai_provider import OpenAIProvider

if __name__ == "__main__":
    llm = OpenAIProvider(api_key="your_api_key_here", base_url="https://openrouter.ai/api/v1", model="meta-llama/llama-4-maverick:free")
    askDb = AskMyDB(db_url="sqlite:///IMDB.db", llm=llm)
    query, result = askDb.ask("get the movies on action genre with rating more than 5 sort it high to low")
    print(query, result)
```

## License

This project is licensed under the MIT License.

## Author and Repository

Author: Shanthosh  
Email: shanthubolt@gmail.com  
Repository: [https://github.com/Msalways/Ask-My-DB](https://github.com/Msalways/Ask-My-DB)

## Custom LLM Provider Example

You can create your own custom LLM provider by subclassing `LLMProvider`. Below is an example implementation of a `CustomProvider`:

```python
from askmydb.llm.base import LLMProvider
from askmydb.llm.sql_prompt import build_sql_prompt, build_system_prompt

class CustomProvider(LLMProvider):
    def __init__(self, base_url, model, temperature):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature

    def generate_sql(self, prompt: str, schema: str) -> str:
        system_prompt = build_system_prompt()
        full_prompt = build_sql_prompt(prompt, schema)
        # Implement your custom logic here to generate the SQL query using your LLM
        query = None
        return query
```

### Using CustomProvider

```python
from askmydb import AskMyDB
from my_custom_provider import CustomProvider

if __name__ == "__main__":
    llm = CustomProvider(base_url="your_base_url", model="your_model", temperature=0.7)
    askDb = AskMyDB(db_url="sqlite:///IMDB.db", llm=llm)
    query, result = askMyDB.ask("get the movies on action genre with rating more than 5 sort it high to low")
    print(query, result)
```
