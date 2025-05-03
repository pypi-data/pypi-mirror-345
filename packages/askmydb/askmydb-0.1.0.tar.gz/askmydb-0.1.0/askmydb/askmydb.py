from askmydb.sql.executor import execute_sql
from askmydb.schema.loader import load_schema
from askmydb.llm.base import LLMProvider


class AskMyDB:
    def __init__(self, db_url: str, llm: LLMProvider):
        """        
        Core class for AskDB.

        Args:
            db_url (str): _database URL_.
            llm (LLMProvider): _LLM provider_.
        """
        self.db_url = db_url
        self.llm = llm
        try:
            self.schema = load_schema(db_url)
        except Exception as e:
            raise RuntimeError(f"AskDB.__init__ error loading schema: {e}") from e
    
    def ask(self, prompt: str) -> list[dict]:
        """
        Ask the database a question.
        Args:
            prompt (str): _question_.
        Returns:
            list[dict]: _list of answers_.
        """
        try:
            sql_query = self.llm.generate_sql(prompt,self.schema)
            # print(f"SQL Query: {sql_query}")
            results = execute_sql(sql_query, self.db_url)
            return sql_query,results
        except Exception as e:
            raise RuntimeError(f"AskMyDB: {e}") from e
