import sqlite3
from typing import Optional, Dict, List

class SQLiteStorage:
    def __init__(self, db_path: str = 'bot.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def execute(self, query: str, params: tuple = ()):
        with self.conn:
            return self.conn.execute(query, params)

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        return self.execute(query, params).fetchone()

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        return self.execute(query, params).fetchall()

    def close(self):
        self.conn.close()