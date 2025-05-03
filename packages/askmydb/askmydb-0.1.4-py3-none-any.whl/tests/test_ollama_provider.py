import pytest

from askmydb.llm.ollama_provider import OllamaProvider

@pytest.fixture
def ollama_provider():
    """
    Fixture to create an instance of the OllamaProvider class.
    """
    return OllamaProvider(base_url="http://localhost:32768", model="qwen2.5:1.5b")

def test_generate_sql_basic(ollama_provider):
    """
    Test the generate_sql method with a basic query.
    """
    
    schema = """
    Table: users
      Column: id - Type: INTEGER
      Column: name - Type: TEXT
    """
    query = "Get all users"
    
    sql = ollama_provider.generate_sql(query,schema=schema)
    
    assert isinstance(sql,str), "SQL should be a string"
    assert "SELECT" in sql.upper(), "SQL query should contain SELECT statement"
    assert "FROM" in sql.upper(), "SQL query should contain FROM statement"

def test_invalid_schema_handling(ollama_provider):
    """
    Test the generate_sql method with an invalid schema.
    """
    
    schema = """

    """
    query = "Get all users"
    
    sql = ollama_provider.generate_sql(query,schema=schema)
    
    assert isinstance(sql,str), "SQL should be a string"