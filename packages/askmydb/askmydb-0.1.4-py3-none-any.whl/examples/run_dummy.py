# examples/run_local.py

import os
import sqlite3

from askmydb import AskMyDB
from askmydb.llm.dummy import DummyLLM


# Create in-memory SQLite DB and populate it
db_url = "sqlite:///test.db"

def setup_sample_db():
    conn = sqlite3.connect("test.db")
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    cur.execute("INSERT INTO users (name, age) VALUES ('Alice', 30), ('Bob', 25)")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_sample_db()

    db = AskMyDB(db_url=db_url, llm=DummyLLM())
    result = db.ask("Get all users")
    print("[📊 Result]:", result)
