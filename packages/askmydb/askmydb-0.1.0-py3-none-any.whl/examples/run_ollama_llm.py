
from askmydb import AskMyDB
from askmydb.llm.ollama_provider import OllamaProvider


if __name__ == "__main__":
    llm = OllamaProvider(base_url="http://localhost:32768", model="qwen2.5:1.5b")
    AskMyDB = AskMyDB(db_url="sqlite:///IMDB.db",llm=llm)
    qwery,result = AskMyDB.ask("get the movies on action genre with rating more than 5 sort it high to low")
    print(result)