import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

PATH = ":memory:" if os.getenv("DB_PATH") == "" else os.getenv("DB_PATH")

DB = sqlite3.connect(PATH)

DB.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT,
    response TEXT
)
""")

DB.commit()
